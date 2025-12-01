import boto3
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_FILE = os.path.join(BASE_DIR, "services.json")

with open(SERVICES_FILE, "r") as f:
    services = json.load(f)

EC2_INSTANCE_ID = "i-0a4c9a98abc46f401"
ssm = boto3.client('ssm')

# ---------------------------------------------------------
# Get all running containers status (unchanged)
# ---------------------------------------------------------
def get_status():
    response = ssm.send_command(
        InstanceIds=[EC2_INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands': ["docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'"]
        }
    )

    command_id = response['Command']['CommandId']
    time.sleep(2)

    output = ssm.get_command_invocation(
        CommandId=command_id,
        InstanceId=EC2_INSTANCE_ID
    )

    return output['StandardOutputContent']


# ---------------------------------------------------------
# ✅ FIXED FUNCTION — CORRECT HEALTH CHECK LOGIC
# ---------------------------------------------------------
def get_single_status(service_name):
    cmd = f"docker inspect -f '{{{{.State.Running}}}}|{{{{.State.StartedAt}}}}' {service_name} 2>/dev/null || echo false|NA"

    response = ssm.send_command(
        InstanceIds=[EC2_INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [cmd]},
    )

    command_id = response['Command']['CommandId']
    time.sleep(2)

    output = ssm.get_command_invocation(
        CommandId=command_id,
        InstanceId=EC2_INSTANCE_ID,
    )

    raw = output['StandardOutputContent'].strip()

    # Normalization for app.py
    if raw.startswith("true|"):
        return raw.replace("true", "running", 1)

    if raw.startswith("false"):
        return "not_running|NA"

    return "not_running|NA"


