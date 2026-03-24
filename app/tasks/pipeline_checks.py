"""
Detect broken/failed pipeline builds and report on pipeline health.
"""
from datetime import datetime
from typing import Optional

from clients.devops_client import DevOpsClient
from config import DEVOPS_PROJECT
from utils.logger import get_logger

log = get_logger()

# Default lookback period in hours
DEFAULT_LOOKBACK_HOURS = 24


def find_failed_builds(
    project: Optional[str] = None,
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS,
    definition_ids: Optional[list[int]] = None
) -> list[dict]:
    """
    Find failed builds within the lookback period.
    
    Args:
        project: Azure DevOps project name
        lookback_hours: How far back to search for failures
        definition_ids: Optional list of specific definition IDs to check
    
    Returns:
        List of failed build details
    """
    project = project or DEVOPS_PROJECT
    client = DevOpsClient()
    
    # Get failed builds
    builds_response = client.get_failed_builds(project=project, top=100)
    builds = builds_response.get("value", [])
    
    # Filter by lookback period
    cutoff = datetime.utcnow().timestamp() - (lookback_hours * 3600)
    recent_failures = []
    
    for build in builds:
        start_time = build.get("startTime")
        if start_time:
            build_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if build_time.timestamp() > cutoff:
                # Filter by definition IDs if specified
                if definition_ids is None or build.get("definition", {}).get("id") in definition_ids:
                    recent_failures.append(build)
    
    log.info(f"Found {len(recent_failures)} failed builds in the last {lookback_hours} hours")
    
    return recent_failures


def analyze_build_failure(build: dict) -> dict:
    """Extract useful information from a failed build."""
    return {
        "id": build.get("id"),
        "definition_name": build.get("definition", {}).get("name", "Unknown"),
        "definition_id": build.get("definition", {}).get("id"),
        "build_number": build.get("buildNumber"),
        "status": build.get("status"),
        "result": build.get("result"),
        "requested_by": build.get("requestedBy", {}).get("displayName", "Unknown"),
        "requested_for": build.get("requestedFor", {}).get("displayName", "Unknown"),
        "start_time": build.get("startTime"),
        "finish_time": build.get("finishTime"),
        "duration_seconds": build.get("duration"),
        "source_branch": build.get("sourceBranch"),
        "source_version": build.get("sourceVersion"),
        "url": build.get("url"),
        "queue_time": build.get("queueTime"),
    }


def print_failed_builds(failures: list[dict], lookback_hours: int = DEFAULT_LOOKBACK_HOURS):
    """Pretty print failed build report."""
    if not failures:
        log.info("No failed builds found! 🎉")
        return
    
    log.info(f"\n{'='*80}")
    log.info(f"BROKEN PIPELINE REPORT (failures in last {lookback_hours} hours)")
    log.info(f"{'='*80}")
    
    # Group by definition
    by_definition = {}
    for failure in failures:
        def_name = failure.get("definition_name", "Unknown")
        if def_name not in by_definition:
            by_definition[def_name] = []
        by_definition[def_name].append(failure)
    
    for def_name, builds in by_definition.items():
        log.info(f"\n📁 {def_name} ({len(builds)} failure(s))")
        log.info("-" * 60)
        
        for build in builds:
            log.info(f"   Build #{build['build_number']}")
            log.info(f"   🔗 {build['url']}")
            log.info(f"   Requested by: {build['requested_by']}")
            log.info(f"   Branch: {build['source_branch']}")
            log.info(f"   Started: {build['start_time']}")
            if build.get("finish_time"):
                log.info(f"   Finished: {build['finish_time']}")
    
    log.info(f"\n{'='*80}")
    log.info(f"SUMMARY: {len(failures)} failed build(s) across {len(by_definition)} pipeline(s)")
    log.info(f"{'='*80}")


def run_pipeline_check(
    project: Optional[str] = None,
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS,
    include_logs: bool = False
) -> list[dict]:
    """
    CLI entry point for pipeline health check.
    
    Args:
        project: Project name override
        lookback_hours: Hours to look back for failures
        include_logs: Whether to fetch and include build logs
    """
    project = project or DEVOPS_PROJECT
    log.info(f"Checking pipeline health for project: {project}")
    log.info(f"Looking back: {lookback_hours} hours")
    
    failures = find_failed_builds(project=project, lookback_hours=lookback_hours)
    
    # Analyze each failure
    analyzed = [analyze_build_failure(f) for f in failures]
    
    print_failed_builds(analyzed, lookback_hours)
    
    return analyzed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Check for failed pipeline builds")
    parser.add_argument("--project", type=str, help="Project name override")
    parser.add_argument("--hours", type=int, default=DEFAULT_LOOKBACK_HOURS,
                        help=f"Hours to look back (default: {DEFAULT_LOOKBACK_HOURS})")
    parser.add_argument("--logs", action="store_true", help="Include build logs (slower)")
    args = parser.parse_args()
    
    run_pipeline_check(
        project=args.project,
        lookback_hours=args.hours,
        include_logs=args.logs
    )
