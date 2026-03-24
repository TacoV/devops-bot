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

    def get_bugs(self, project=None):
        """Get all active bugs, optionally filtered by project name."""
        project = project or DEVOPS_PROJECT
        wiql_url = f"{self.base_url}/{DEVOPS_PROJECTID}/_apis/wit/wiql?api-version=7.0"

        query = {
            "query": f"""
                SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.Priority], [System.ChangedDate]
                FROM WorkItems
                WHERE
                    [System.TeamProject] = '{project}'
                    AND [System.WorkItemType] = 'Bug'
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

    def get_work_items(self, ids, fields=None):
        """Get work items by IDs with optional field selection."""
        ids_str = ",".join(map(str, ids))
        fields_str = ",".join(fields) if fields else None
        url = f"{self.base_url}/_apis/wit/workitemsbatch?api-version=7.0"
        
        payload = {
            "ids": ids,
            "$expand": "fields"
        }
        if fields_str:
            payload["fields"] = fields_str

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
        
        query = {
            "query": wiql_query
        }
        
        r = self.session.post(wiql_url, json=query)
        r.raise_for_status()
        ids = [item["id"] for item in r.json().get("workItems", [])]
        
        if not ids:
            return []
        
        return self.get_work_items(ids)

    # === Pipeline Methods ===
    
    def get_build_definitions(self, project: str = None):
        """Get all build definitions for a project."""
        project = project or DEVOPS_PROJECT
        url = f"{self.base_url}/{project}/_apis/build/definitions?api-version=7.0"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def get_builds(self, project: str = None, definitions: list[int] = None, 
                   result_filter: str = None, top: int = 100):
        """
        Get recent builds, optionally filtered by definition or result.
        
        Args:
            project: Project name
            definitions: List of build definition IDs
            result_filter: Filter by result (e.g., 'failed', 'succeeded')
            top: Number of builds to return
        """
        project = project or DEVOPS_PROJECT
        url = f"{self.base_url}/{project}/_apis/build/builds?api-version=7.0&top={top}"
        
        if definitions:
            definitions_str = ";".join(map(str, definitions))
            url += f"&definitions={definitions_str}"
        
        if result_filter:
            url += f"&resultFilter={result_filter}"
        
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def get_failed_builds(self, project: str = None, top: int = 50):
        """Get recent failed builds."""
        return self.get_builds(project=project, result_filter="failed", top=top)

    def get_build_summary(self, build_id: int, project: str = None) -> dict:
        """Get summary details for a specific build."""
        project = project or DEVOPS_PROJECT
        url = f"{self.base_url}/{project}/_apis/build/builds/{build_id}?api-version=7.0"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def get_build_logs(self, build_id: int, project: str = None, timeline_url: str = None):
        """
        Get build logs. Can use timeline_url to get logs for specific tasks.
        """
        project = project or DEVOPS_PROJECT
        
        # Get timeline to find log URLs
        if not timeline_url:
            timeline_url = f"{self.base_url}/{project}/_apis/build/builds/{build_id}/timeline"
        
        r = self.session.get(timeline_url)
        if r.status_code == 204:
            # Logs not yet available or not configured
            return None
        
        r.raise_for_status()
        timeline = r.json()
        
        # Get log for each task
        logs = []
        for record in timeline.get("records", []):
            if record.get("type") == "Task" and record.get("logUrl"):
                task_name = record.get("name", "Unknown")
                log_r = self.session.get(record["logUrl"])
                if log_r.status_code == 200:
                    logs.append({
                        "task": task_name,
                        "content": log_r.text
                    })
        
        return logs if logs else None