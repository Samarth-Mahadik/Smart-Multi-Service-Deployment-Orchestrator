# health_check.py
import os
import json
import boto3
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_FILE = os.path.join(BASE_DIR, "services.json")
REMOTE_LOG_DIR = "/home/ubuntu/smso_logs"
REMOTE_LOG_FILE = os.path.join(REMOTE_LOG_DIR, "health_log.json")
LOCAL_SUMMARY = os.path.join(BASE_DIR, "health_summary.json")
INSTANCE_ID = "i-0a4c9a98abc46f401"

ssm = boto3.client("ssm")

def run_ssm(commands):
    response = ssm.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands},
    )
    cmd_id = response["Command"]["CommandId"]
    time.sleep(2)
    return ssm.get_command_invocation(CommandId=cmd_id, InstanceId=INSTANCE_ID)

def parse_host_port(port_mapping):
    return int(port_mapping.split(":")[0]) if ":" in port_mapping else int(port_mapping)

def ensure_remote_logdir():
    cmd = [f"mkdir -p {REMOTE_LOG_DIR}", f"touch {REMOTE_LOG_FILE}"]
    run_ssm(cmd)

def append_remote_log(entry):
    js = json.dumps(entry)
    cmd = [f"python3 - <<'PY'\nimport json\nf = open('{REMOTE_LOG_FILE}','a')\nf.write(json.dumps({entry}) + '\\n')\nPY"]
    # simpler: echo line to file
    cmd = [f"echo '{js}' >> {REMOTE_LOG_FILE}"]
    run_ssm(cmd)

def check_and_recover():
    with open(SERVICES_FILE, "r") as f:
        services = json.load(f)

    ensure_remote_logdir()
    summary = []
    for s in services:
        name = s["name"]
        host_port = parse_host_port(s["port"])
        # Health check
        health_cmd = f"bash -lc \"curl -sS --fail --max-time 5 http://localhost:{host_port}/healthz || echo __HEALTH_FAIL__\""
        out = run_ssm([health_cmd])
        health_stdout = out.get("StandardOutputContent", "").strip()
        record = {"service": name, "time": int(time.time()), "health": health_stdout}
        if "__HEALTH_FAIL__" in health_stdout or health_stdout == "":
            # attempt rollback to stable image if exists
            # check for stable image
            check_stable = run_ssm([f"docker images -q {name}_stable || true"])
            stable_image_id = check_stable.get("StandardOutputContent", "").strip()
            if stable_image_id:
                cmds = [
                    f"sudo docker stop {name} || true",
                    f"sudo docker rm {name} || true",
                    f"sudo docker run -d --name {name} -p {s['port']} {name}_stable"
                ]
                rb_out = run_ssm(cmds)
                record["action"] = "rolled_back_to_stable"
                record["result"] = rb_out.get("StandardOutputContent", "") + rb_out.get("StandardErrorContent", "")
            else:
                record["action"] = "no_stable_image"
                record["result"] = "No stable image to rollback"
        else:
            record["action"] = "healthy"
            record["result"] = health_stdout

        append_remote_log(record)
        summary.append(record)

    # write local summary
    with open(LOCAL_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)

    return "Health check completed."

if __name__ == "__main__":
    print(check_and_recover())
