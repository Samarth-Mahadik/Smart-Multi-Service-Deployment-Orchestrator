import boto3

EC2_INSTANCE_ID = "i-0a4c9a98abc46f401"
ssm = boto3.client('ssm')

def stop_all_containers():
    cmd = "docker stop $(docker ps -aq) || true"
    ssm.send_command(
        InstanceIds=[EC2_INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [cmd]}
    )
    return "All services stopped successfully."

def stop_single(service_name):
    cmd = f"docker stop {service_name} || true && docker rm {service_name} || true"
    ssm.send_command(
        InstanceIds=[EC2_INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [cmd]}
    )
    return f"{service_name} stopped (if running)."
