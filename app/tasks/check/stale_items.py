"""
Check for stale work items that haven't been updated in a configurable number of days.
"""
from datetime import datetime, timedelta
from typing import Optional

from clients.devops_client import DevOpsClient
from config.env import DEVOPS_PROJECT
from utils.logger import get_logger

log = get_logger()


def run_check(days: int = 14) -> str:
    """
    Find work items that haven't been updated in the specified number of days.
    
    Args:
        days: Number of days after which an item is considered stale (default: 14)
    
    Returns:
        List of stale work items with their details
    """
    client = DevOpsClient()
    
    query = f"""
        SELECT [System.Id]
        FROM WorkItems
        WHERE
            [System.TeamProject] = '{DEVOPS_PROJECT}'
            AND [System.ChangedDate] < @today - {days}
        ORDER BY [System.ChangedDate] ASC
    """
    
    stale_items = client.get_work_items_by_query(query)
    
    result = format_results(stale_items)
    log.info(result)

    return result

def format_results(items: list[dict], days: int = 14):
    """Pretty print stale work items."""
    if not items:
        return "No stale items found!"
    
    report = f"\n{'='*60}"
    report += f"STALE ITEMS REPORT (not updated in {days}+ days)"
    report += f"{'='*60}"
    
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
        
        report += f"\n#{item_id} | {work_item_type} | {state}"
        report += f"   Title: {title}"
        report += f"   Assigned: {assigned_to}"
        report += f"   Priority: {priority}"
        report += f"   Last Updated: {changed_date}"
    
    report += f"\n{'='*60}"
    report += f"Total: {len(items)} stale items"

    return report
