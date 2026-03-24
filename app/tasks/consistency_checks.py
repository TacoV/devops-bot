"""
Work item consistency checks for board hygiene.

These checks identify common issues like:
- Completed parents with open children
- Active items without children
- Items missing estimates
- Priority mismatches

All checks respect team-specific configuration from TeamConfig.
"""
from typing import Optional
from clients.devops_client import DevOpsClient
from config import DEVOPS_PROJECT, default_team
from utils.logger import get_logger

log = get_logger()


def _get_work_items_with_relations(client: DevOpsClient, project: str) -> tuple[list[dict], dict]:
    """
    Fetch all work items with their parent-child relationships.
    
    Returns:
        Tuple of (items list, relations dict {child_id: parent_id})
    """
    # Query all work items with relation fields
    query = f"""
        SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType],
               [System.AssignedTo], [System.ChangedDate], [System.Priority],
               [System.Parent]
        FROM WorkItems
        WHERE [System.TeamProject] = '{project}'
    """
    
    items = client.get_work_items_by_query(query, project)
    
    # Build parent-child relations
    relations = {}
    for item in items:
        fields = item.get("fields", {})
        parent_ref = fields.get("System.Parent")
        if parent_ref:
            # Parent is a reference link
            parent_id = parent_ref.get("id") if isinstance(parent_ref, dict) else None
            if parent_id:
                relations[item["id"]] = parent_id
    
    return items, relations


def check_orphaned_children(team: Optional[object] = None) -> list[dict]:
    """
    Find completed parents with active children.
    
    Example: User Story is Closed but Tasks are still Active.
    """
    team = team or default_team
    client = DevOpsClient()
    project = DEVOPS_PROJECT
    
    items, relations = _get_work_items_with_relations(client, project)
    
    # Build item lookup
    items_by_id = {item["id"]: item for item in items}
    
    # Build children lookup: parent_id -> [child_ids]
    children_by_parent = {}
    for child_id, parent_id in relations.items():
        if parent_id not in children_by_parent:
            children_by_parent[parent_id] = []
        children_by_parent[parent_id].append(child_id)
    
    issues = []
    completed_states = set(team.completed_states)
    
    for item in items:
        fields = item.get("fields", {})
        state = fields.get("System.State", "")
        
        if state in completed_states:
            # This item is completed - check children
            child_ids = children_by_parent.get(item["id"], [])
            for child_id in child_ids:
                child = items_by_id.get(child_id)
                if child:
                    child_state = child.get("fields", {}).get("System.State", "")
                    if child_state not in completed_states:
                        issues.append({
                            "type": "orphaned_child",
                            "parent_id": item["id"],
                            "parent_title": fields.get("System.Title", ""),
                            "parent_state": state,
                            "child_id": child_id,
                            "child_title": child.get("fields", {}).get("System.Title", ""),
                            "child_state": child_state,
                        })
    
    return issues


def check_empty_parents(team: Optional[object] = None) -> list[dict]:
    """
    Find active parents without child tasks.
    
    Example: User Story is Active but has no Tasks.
    """
    team = team or default_team
    client = DevOpsClient()
    project = DEVOPS_PROJECT
    
    items, relations = _get_work_items_with_relations(client, project)
    
    # Build children lookup: parent_id -> [child_ids]
    children_by_parent = {}
    for child_id, parent_id in relations.items():
        if parent_id not in children_by_parent:
            children_by_parent[parent_id] = []
        children_by_parent[parent_id].append(child_id)
    
    issues = []
    active_states = set(team.active_states)
    
    for item in items:
        fields = item.get("fields", {})
        state = fields.get("System.State", "")
        work_type = fields.get("System.WorkItemType", "")
        
        # Check if this type should have children
        child_types = team.hierarchy_rules.get(work_type, [])
        
        if state in active_states and child_types:
            # This item should have children - does it?
            child_ids = children_by_parent.get(item["id"], [])
            if not child_ids:
                issues.append({
                    "type": "empty_parent",
                    "item_id": item["id"],
                    "title": fields.get("System.Title", ""),
                    "state": state,
                    "work_item_type": work_type,
                    "expected_children": child_types,
                })
    
    return issues


def check_missing_estimates(team: Optional[object] = None) -> list[dict]:
    """
    Find items missing effort/st point estimates.
    """
    team = team or default_team
    client = DevOpsClient()
    project = DEVOPS_PROJECT
    
    items, _ = _get_work_items_with_relations(client, project)
    
    issues = []
    
    for item in items:
        fields = item.get("fields", {})
        work_type = fields.get("System.WorkItemType", "")
        
        # Only check types that typically have estimates
        estimate_types = team.hierarchy_rules.keys()
        
        if work_type in estimate_types:
            # Check common estimate fields
            has_estimate = any([
                fields.get("Microsoft.VSTS.Scheduling.StoryPoints"),
                fields.get("Microsoft.VSTS.Scheduling.Effort"),
                fields.get("Microsoft.VSTS.Scheduling.RemainingWork"),
            ])
            
            if not has_estimate:
                issues.append({
                    "type": "missing_estimate",
                    "item_id": item["id"],
                    "title": fields.get("System.Title", ""),
                    "state": fields.get("System.State", ""),
                    "work_item_type": work_type,
                })
    
    return issues


def check_priority_mismatch(team: Optional[object] = None) -> list[dict]:
    """
    Find children with higher priority than parents.
    
    In Azure DevOps, lower number = higher priority (1=Critical, 4=Low).
    """
    team = team or default_team
    client = DevOpsClient()
    project = DEVOPS_PROJECT
    
    items, relations = _get_work_items_with_relations(client, project)
    
    # Build item lookup
    items_by_id = {item["id"]: item for item in items}
    
    issues = []
    
    for child_id, parent_id in relations.items():
        child = items_by_id.get(child_id)
        parent = items_by_id.get(parent_id)
        
        if child and parent:
            child_priority = child.get("fields", {}).get("System.Priority")
            parent_priority = parent.get("fields", {}).get("System.Priority")
            
            if child_priority and parent_priority:
                # Child priority should be >= parent priority (lower number = higher priority)
                # If child has lower number (higher priority), that's a mismatch
                if child_priority < parent_priority:
                    issues.append({
                        "type": "priority_mismatch",
                        "parent_id": parent_id,
                        "parent_title": parent.get("fields", {}).get("System.Title", ""),
                        "parent_priority": parent_priority,
                        "child_id": child_id,
                        "child_title": child.get("fields", {}).get("System.Title", ""),
                        "child_priority": child_priority,
                    })
    
    return issues


def run_consistency_checks(team: Optional[object] = None, verbose: bool = True) -> dict:
    """
    Run all consistency checks and return results.
    
    Returns:
        Dict with check results: {"orphaned_children": [...], "empty_parents": [...], ...}
    """
    team = team or default_team
    log.info("Running work item consistency checks...")
    
    results = {
        "orphaned_children": check_orphaned_children(team),
        "empty_parents": check_empty_parents(team),
        "missing_estimates": check_missing_estimates(team),
        "priority_mismatch": check_priority_mismatch(team),
    }
    
    total_issues = sum(len(v) for v in results.values())
    
    if verbose:
        _print_results(results)
    
    log.info(f"\nTotal issues found: {total_issues}")
    
    return results


def _print_results(results: dict):
    """Pretty print consistency check results."""
    
    if results["orphaned_children"]:
        log.info(f"\n{'='*60}")
        log.info(f"🔴 Orphaned Children ({len(results['orphaned_children'])})")
        log.info("Completed parents with active children:")
        for issue in results["orphaned_children"][:10]:
            log.info(f"  #{issue['parent_id']} ({issue['parent_state']}): {issue['parent_title'][:40]}")
            log.info(f"    └─ #{issue['child_id']} ({issue['child_state']}): {issue['child_title'][:40]}")
        if len(results["orphaned_children"]) > 10:
            log.info(f"  ... and {len(results['orphaned_children']) - 10} more")
    
    if results["empty_parents"]:
        log.info(f"\n{'='*60}")
        log.info(f"🟡 Empty Parents ({len(results['empty_parents'])})")
        log.info("Active items without child tasks:")
        for issue in results["empty_parents"][:10]:
            log.info(f"  #{issue['item_id']} ({issue['work_item_type']}): {issue['title'][:50]}")
        if len(results["empty_parents"]) > 10:
            log.info(f"  ... and {len(results['empty_parents']) - 10} more")
    
    if results["missing_estimates"]:
        log.info(f"\n{'='*60}")
        log.info(f"🟠 Missing Estimates ({len(results['missing_estimates'])})")
        log.info("Items without effort/story points:")
        for issue in results["missing_estimates"][:10]:
            log.info(f"  #{issue['item_id']} ({issue['work_item_type']}): {issue['title'][:50]}")
        if len(results["missing_estimates"]) > 10:
            log.info(f"  ... and {len(results['missing_estimates']) - 10} more")
    
    if results["priority_mismatch"]:
        log.info(f"\n{'='*60}")
        log.info(f"🔵 Priority Mismatch ({len(results['priority_mismatch'])})")
        log.info("Children with higher priority than parents:")
        for issue in results["priority_mismatch"][:10]:
            log.info(f"  Parent #{issue['parent_id']} (P{issue['parent_priority']}): {issue['parent_title'][:30]}")
            log.info(f"    └─ Child #{issue['child_id']} (P{issue['child_priority']}): {issue['child_title'][:30]}")
        if len(results["priority_mismatch"]) > 10:
            log.info(f"  ... and {len(results['priority_mismatch']) - 10} more")
    
    if not any(results.values()):
        log.info("\n✅ No consistency issues found!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run work item consistency checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    run_consistency_checks(verbose=args.verbose)
