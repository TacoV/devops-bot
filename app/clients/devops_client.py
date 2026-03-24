"""
Azure DevOps REST API client for work item operations.
"""
import requests
from config import DEVOPS_URL, DEVOPS_PROJECT, DEVOPS_TOKEN, DEVOPS_PROJECTID


class DevOpsClient:
    """Client for Azure DevOps REST API operations."""
    
    def __init__(self):
        self.base_url = DEVOPS_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {DEVOPS_TOKEN}",
            "Content-Type": "application/json"
        })

    def get_bugs(self, project=None):
        """Get all active bugs, optionally filtered by project name."""
        project = project or DEVOPS_PROJECT
        
        wiql = f"""
            SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.Priority], [System.ChangedDate]
            FROM WorkItems
            WHERE
                [System.TeamProject] = '{project}'
                AND [System.WorkItemType] = 'Bug'
                AND [System.State] <> 'Closed'
            ORDER BY [System.ChangedDate] DESC
        """
        
        return self.get_work_items_by_query(wiql, project)

    def get_work_items(self, ids, fields=None):
        """Get work items by IDs with optional field selection."""
        if not ids:
            return []
            
        ids_str = ",".join(map(str, ids))
        url = f"{self.base_url}/_apis/wit/workitemsbatch?api-version=7.0"
        
        payload = {
            "ids": ids,
            "$expand": "fields"
        }
        if fields:
            payload["fields"] = fields

        r = self.session.post(url, json=payload)
        r.raise_for_status()
        return r.json().get("value", [])

    def get_projects(self):
        """Get all projects in the organization."""
        url = f"{self.base_url}/_apis/projects?api-version=7.0&stateFilter=WellFormed"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def get_work_items_by_query(self, wiql_query, project=None):
        """Execute a WIQL query and return work items."""
        project = project or DEVOPS_PROJECTID
        wiql_url = f"{self.base_url}/{project}/_apis/wit/wiql?api-version=7.0"
        
        query = {"query": wiql_query}
        
        r = self.session.post(wiql_url, json=query)
        r.raise_for_status()
        ids = [item["id"] for item in r.json().get("workItems", [])]
        
        if not ids:
            return []
        
        return self.get_work_items(ids)
