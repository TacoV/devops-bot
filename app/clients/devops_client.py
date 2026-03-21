import base64
import requests
from config import DEVOPS_URL, DEVOPS_PROJECT, DEVOPS_TOKEN, DEVOPS_PROJECTID

class DevOpsClient:
    def __init__(self):
        self.base_url = DEVOPS_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {DEVOPS_TOKEN}",
            "Content-Type": "application/json"
        })

    def get_bugs(self):
        wiql_url = f"{DEVOPS_URL}/{DEVOPS_PROJECTID}/_apis/wit/wiql?api-version=7.0"

        query = {
            "query": f"""
                SELECT [System.Id]
                FROM WorkItems
                WHERE
                    [System.TeamProject] = '{DEVOPS_PROJECT}'
                    AND [System.WorkItemType] <> 'Bug'
                    AND [System.State] <> 'Closed'
                ORDER BY [System.ChangedDate] DESC
            """
        }

        r = self.session.post(wiql_url, json=query)
        r.raise_for_status()
        ids = [item["id"] for item in r.json().get("workItems", [])]

        if not ids:
            return []

        return self.get_work_items(ids)

    def get_work_items(self, ids):
        ids_str = ",".join(map(str, ids))
        url = f"{self.base_url}/_apis/wit/workitems?ids={ids_str}&api-version=7.0"

        r = self.session.get(url)
        r.raise_for_status()
        return r.json().get("value", [])