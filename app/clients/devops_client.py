import requests
from config import DEVOPS_URL, DEVOPS_TOKEN

class DevOpsClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {DEVOPS_TOKEN}",
            "Content-Type": "application/json"
        })

    def get_projects(self):
        r = self.session.get(f"{DEVOPS_URL}/_apis/projects")
        r.raise_for_status()
        return r.json()

    def get_tickets(self):
        r = self.session.get(f"{DEVOPS_URL}")