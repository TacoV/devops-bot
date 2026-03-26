"""
Check for stale work items that haven't been updated in a configurable number of days.
"""
from datetime import datetime, timedelta
from typing import Optional

from clients.devops_client import DevOpsClient
from config import DEVOPS_PROJECT
from utils.logger import get_logger

log = get_logger()


def run_check(days: int = 14, project: Optional[str] = None) -> list[dict]:
    """
    Find work items that haven't been updated in the specified number of days.
    
    Args:
        days: Number of days after which an item is considered stale (default: 14)
        project: Azure DevOps project name (defaults to config value)
    
    Returns:
        List of stale work items with their details
    """
    project = project or DEVOPS_PROJECT
    client = DevOpsClient()
    
    query = f"""
        SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], 
               [System.AssignedTo], [System.ChangedDate], [System.CreatedDate], [System.Priority]
        FROM WorkItems
        WHERE
            [System.TeamProject] = '{project}'
            AND [System.ChangedDate] < @today - {days}
        ORDER BY [System.ChangedDate] ASC
    """
    
    stale_items = client.get_work_items_by_query(query, project)
    
    log.info(f"Found {len(stale_items)} stale items (not updated in {days}+ days)")
    
    return stale_items


def print_results(items: list[dict], days: int = 14):
    """Pretty print stale work items."""
    if not items:
        log.info("No stale items found!")
        return
    
    log.info(f"\n{'='*80}")
    log.info(f"STALE ITEMS REPORT (not updated in {days}+ days)")
    log.info(f"{'='*80}")
    
    for item in items:
        fields = item.get("fields", {})
        item_id = item.get("id")
        title = fields.get("System.Title", "No title")
        state = fields.get("System.State", "Unknown")
        work_item_type = fields.get("System.WorkItemType", "Unknown")
        assigned_to = fields.get("System.AssignedTo", "Unassigned")
        changed_date = fields.get("System.ChangedDate", "Unknown")
        priority = fields.get("System.Priority", "Not set")
        
        # Handle AssignedTo potentially being a dict (Azure DevOps format)
        if isinstance(assigned_to, dict):
            assigned_to = assigned_to.get("displayName", "Unassigned")
        
        log.info(f"\n#{item_id} | {work_item_type} | {state}")
        log.info(f"   Title: {title}")
        log.info(f"   Assigned: {assigned_to}")
        log.info(f"   Priority: {priority}")
        log.info(f"   Last Updated: {changed_date}")
    
    log.info(f"\n{'='*80}")
    log.info(f"Total: {len(items)} stale items")
