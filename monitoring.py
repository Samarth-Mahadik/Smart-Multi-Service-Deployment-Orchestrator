# monitoring.py
import boto3
import time
import json
import os
from botocore.exceptions import ClientError

EC2_INSTANCE_ID = "i-0a4c9a98abc46f401"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEPLOY_LOG = os.path.join(BASE_DIR, "deploy_status.json")

ssm = boto3.client("ssm")


def safe_ssm_execute(cmd):
    """Prevent app crash when instance is stopped"""
    try:
        resp = ssm.send_command(
            InstanceIds=[EC2_INSTANCE_ID],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": [cmd]},
        )
        cmd_id = resp["Command"]["CommandId"]
        time.sleep(2)
        out = ssm.get_command_invocation(CommandId=cmd_id, InstanceId=EC2_INSTANCE_ID)
        return out["StandardOutputContent"].strip()
    except ClientError as e:
        if "InvalidInstanceId" in str(e):
            return "Instance Stopped"
        return f"Error: {e}"


def get_container_uptime(service_name):
    cmd = f"docker ps --filter 'name={service_name}' --format '{{{{.RunningFor}}}}'"
    return safe_ssm_execute(cmd) or "Not Running"


def get_service_version(service_name):
    cmd = f"docker ps --filter 'name={service_name}' --format '{{{{.Image}}}}'"
    return safe_ssm_execute(cmd) or "Unknown"


def get_deployment_history():
    if not os.path.exists(DEPLOY_LOG):
        return []
    with open(DEPLOY_LOG) as f:
        return json.load(f)
