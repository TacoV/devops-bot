from clients.devops_client import DevOpsClient
from utils.logger import get_logger

log = get_logger()

def list_bugs():
    client = DevOpsClient()
    bugs = client.get_bugs()

    log.info(f"Found {len(bugs)} active bugs")

    for b in bugs[:5]:
        fields = b["fields"]
        log.info(
            f"#{b['id']} | {fields['System.Title']} | {fields['System.State']}"
        )