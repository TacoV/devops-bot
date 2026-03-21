from clients.devops_client import DevOpsClient
from utils.logger import get_logger

log = get_logger()

def run_health_checks():
    client = DevOpsClient()
    projects = client.get_projects()
    log.info(f"Found {len(projects.get('value', []))} projects")