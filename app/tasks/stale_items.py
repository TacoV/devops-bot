"""
Detect work items that haven't been updated in a configurable number of days.
"""
from datetime import datetime, timedelta
from typing import Optional

from clients.devops_client import DevOpsClient
from config import DEVOPS_PROJECT, default_team
from utils.logger import get_logger

log = get_logger()


def find_stale_items(
    project: Optional[str] = None,
    days: Optional[int] = None,
    work_item_types: Optional[list[str]] = None,
    states: Optional[list[str]] = None,
    team: Optional[object] = None
) -> list[dict]:
    """
    Find work items that haven't been updated in the specified number of days.
    
    Args:
        project: Azure DevOps project name (defaults to config value)
        days: Number of days after which an item is considered stale (uses team default if not set)
        work_item_types: List of work item types to check (e.g., ['Bug', 'Task'])
        states: List of states to include (e.g., ['Active', 'To Do'])
        team: TeamConfig instance (uses default_team if not provided)
    
    Returns:
        List of stale work items with their details
    """
    team = team or default_team
    project = project or DEVOPS_PROJECT
    client = DevOpsClient()
    
    # Build WIQL query using team configuration
    work_item_filter = ""
    if work_item_types:
        types_str = ", ".join(f"'{wt}'" for wt in work_item_types)
        work_item_filter = f"AND [System.WorkItemType] IN ({types_str})"
    
    state_filter = ""
    if states:
        states_str = ", ".join(f"'{s}'" for s in states)
        state_filter = f"AND [System.State] IN ({states_str})"
    
    # Use team-configured stale threshold if not specified
    if days is None:
        days = team.default_stale_days
    
    query = f"""
        SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], 
               [System.AssignedTo], [System.ChangedDate], [System.CreatedDate], [System.Priority]
        FROM WorkItems
        WHERE
            [System.TeamProject] = '{project}'
            AND [System.ChangedDate] < @today - {days}
            {work_item_filter}
            {state_filter}
        ORDER BY [System.ChangedDate} ASC
    """
    
    stale_items = client.get_work_items_by_query(query, project)
    
    log.info(f"Found {len(stale_items)} stale items (not updated in {days}+ days)")
    
    return stale_items


def print_stale_items(items: list[dict], days: int = 14):
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


def run_stale_check(days: Optional[int] = None, project: Optional[str] = None):
    """CLI entry point for stale item detection."""
    team = default_team
    effective_days = days if days is not None else team.default_stale_days
    
    log.info(f"Checking for items stale for {effective_days} days in project: {project or DEVOPS_PROJECT}")
    items = find_stale_items(project=project, days=effective_days)
    print_stale_items(items, effective_days)
    return items


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find stale work items")
    parser.add_argument("--days", type=int, 
                        help=f"Days threshold (default: {default_team.default_stale_days})")
    parser.add_argument("--project", type=str, help="Project name override")
    args = parser.parse_args()
    run_stale_check(days=args.days, project=args.project)
