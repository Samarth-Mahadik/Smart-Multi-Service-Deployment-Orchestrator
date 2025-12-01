import os
import json
import boto3
import time

# -------------------------
# Config / Paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_FILE = os.path.join(BASE_DIR, "services.json")
LOCAL_STATUS_FILE = os.path.join(BASE_DIR, "deploy_status.json")

INSTANCE_ID = "i-0a4c9a98abc46f401"

ssm = boto3.client("ssm")

# -------------------------
# Helpers
# -------------------------
def run_ssm(commands, timeout_seconds=60):
    response = ssm.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands},
        TimeoutSeconds=timeout_seconds,
    )

    command_id = response["Command"]["CommandId"]

    for _ in range(30):
        time.sleep(2)
        output = ssm.get_command_invocation(
            CommandId=command_id,
            InstanceId=INSTANCE_ID
        )
        if output["Status"] in ("Success", "Failed", "TimedOut", "Cancelled"):
            return output

    return ssm.get_command_invocation(
        CommandId=command_id,
        InstanceId=INSTANCE_ID
    )


def parse_host_port(port_mapping):
    return int(port_mapping.split(":")[0])


def safe_write_local_status(entries):
    try:
        with open(LOCAL_STATUS_FILE, "w") as f:
            json.dump(entries, f, indent=2)
    except Exception:
        pass


def container_running(name):
    check = run_ssm([
        f"docker ps --filter 'name={name}' --format '{{{{.Names}}}}'"
    ])
    return name in check.get("StandardOutputContent", "")


# -------------------------
# Core: Deploy All
# -------------------------
def deploy_containers():
    with open(SERVICES_FILE, "r") as f:
        services = json.load(f)

    status_log = []

    for s in services:
        result = deploy_single_internal(s)

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        if "successfully" not in result.lower():
            status_log.append({
                "service": s["name"],
                "status": "failed",
                "reason": result,
                "timestamp": timestamp
            })

            safe_write_local_status(status_log)
            return f"Deployment stopped: {result}"

        else:
            status_log.append({
                "service": s["name"],
                "status": "deployed",
                "image": s["image"],
                "timestamp": timestamp
            })

    safe_write_local_status(status_log)
    return "All services deployed successfully."


# -------------------------
# Deploy Single
# -------------------------
def deploy_single(service_name):
    with open(SERVICES_FILE, "r") as f:
        services = json.load(f)

    for s in services:
        if s["name"] == service_name:
            return deploy_single_internal(s)

    return f"Service '{service_name}' not found."


# -------------------------
# Internal Logic with fixes
# -------------------------
def deploy_single_internal(s):
    name = s["name"]
    image = s["image"]
    port = s["port"]
    host_port = parse_host_port(port)

    # Pull + Run
    commands = [
        f"sudo docker stop {name} || true",
        f"sudo docker rm {name} || true",
        f"sudo docker pull {image}",
        f"sudo docker run -d --name {name} -p {port} {image}"
    ]
    run_ssm(commands)

    # Wait to allow container startup
    time.sleep(5)

    # ✅ Verify container actually started
    if not container_running(name):
        return f"Deploy failed: {name} container did not start."

    # ✅ Health check
    health = run_ssm([
        f"sudo docker exec {name} curl -sS --fail http://localhost:{host_port}/healthz || echo FAIL"
    ])

    health_out = health.get("StandardOutputContent", "").strip()

    if health_out == "" or health_out == "FAIL":
        run_ssm([
            f"sudo docker stop {name} || true",
            f"sudo docker rm {name} || true"
        ])
        return f"Deploy failed: {name} health check failed."

    # Commit stable snapshot
    run_ssm([f"sudo docker commit {name} {name}_stable || true"])

    return f"{name} deployed successfully."


# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":
    print("Starting full deployment...")
    print(deploy_containers())
