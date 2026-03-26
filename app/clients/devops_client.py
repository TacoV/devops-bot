"""
Azure DevOps REST API client for work item operations.
"""
import requests
import logging
from config.env import DEVOPS_URL, DEVOPS_PROJECT, DEVOPS_TOKEN, DEVOPS_PROJECTID

logger = logging.getLogger()

class DevOpsClient:
    """Client for Azure DevOps REST API operations."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {DEVOPS_TOKEN}",
            "Content-Type": "application/json"
        })

    def get_work_items(self, ids, fields=None):
        """Get work items by IDs with optional field selection."""
        if not ids:
            return []
            
        ids_str = ",".join(map(str, ids))
        url = f"{DEVOPS_URL}/_apis/wit/workitemsbatch?api-version=7.0"
        
        payload = {
            "ids": ids,
            "$expand": "fields"
        }
        if fields:
            payload["fields"] = fields

        r = self.session.post(url, json=payload)
        r.raise_for_status()

        return r.json().get("value", [])

    def get_work_items_by_query(self, wiql_query):
        """Execute a WIQL query and return work items."""
        wiql_url = f"{DEVOPS_URL}/{DEVOPS_PROJECTID}/_apis/wit/wiql?api-version=7.0"
        
        query = {"query": wiql_query}
        
        r = self.session.post(wiql_url, json=query)
        r.raise_for_status()

        ids = [item["id"] for item in r.json().get("workItems", [])]
        
        if not ids:
            return []
        
        return self.get_work_items(ids)
