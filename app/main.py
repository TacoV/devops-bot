"""
DevOps Bot - Azure DevOps automation and LLM-assisted tasks.
"""
import argparse
from typing import Optional

from utils.logger import get_logger
from utils.notifications import (
    format_bug_alert, 
    format_pipeline_alert, 
    format_stale_items_alert,
    HAS_SLACK
)
from llm.summarizer import summarize_bugs, summarize_sprint, summarize_pipeline_failure
from llm.reviewer import rate_work_item_priority

log = get_logger()


def run_health_checks():
    """Run basic health checks against Azure DevOps."""
    from clients.devops_client import DevOpsClient
    from tasks.health_checks import run_health_checks as _run
    
    client = DevOpsClient()
    projects = client.get_projects()
    log.info(f"Found {projects.get('count', 0)} projects")
    
    for project in projects.get('value', [])[:5]:
        log.info(f"  - {project.get('name')}")
    
    if projects.get('count', 0) > 5:
        log.info(f"  ... and {projects.get('count', 0) - 5} more")


def run_bugs():
    """List and optionally summarize active bugs."""
    from tasks.list_bugs import list_bugs as _list_bugs
    from clients.devops_client import DevOpsClient
    
    client = DevOpsClient()
    bugs = client.get_bugs()
    
    log.info(f"Found {len(bugs)} active bugs")
    
    for b in bugs[:10]:
        fields = b.get("fields", {})
        assigned = fields.get("System.AssignedTo", "Unassigned")
        if isinstance(assigned, dict):
            assigned = assigned.get("displayName", "Unassigned")
        
        log.info(
            f"  #{b['id']} | {fields.get('System.Title', 'No title')[:60]} | "
            f"{fields.get('System.State', 'Unknown')} | {assigned}"
        )
    
    # Send to Slack if configured
    if HAS_SLACK:
        format_bug_alert(bugs)
    
    # Generate LLM summary if API key available
    if bugs:
        summary = summarize_bugs(bugs)
        if summary:
            log.info("\n📋 Bug Summary:\n" + summary)


def run_stale(days: int = 14, project: Optional[str] = None, notify: bool = False):
    """Find and report stale work items."""
    from tasks.stale_items import run_stale_check
    
    items = run_stale_check(days=days, project=project)
    
    if notify and HAS_SLACK and items:
        format_stale_items_alert(items, days)
    
    return items


def run_pipeline(hours: int = 24, project: Optional[str] = None, notify: bool = False):
    """Check for failed pipeline builds."""
    from tasks.pipeline_checks import run_pipeline_check
    
    failures = run_pipeline_check(project=project, lookback_hours=hours)
    
    if notify and HAS_SLACK:
        format_pipeline_alert(failures)
    
    return failures


def run_summarize(task: str, item_ids: Optional[str] = None):
    """Summarize work items or pipeline failures using LLM."""
    from clients.devops_client import DevOpsClient
    
    client = DevOpsClient()
    
    if task == "bugs":
        bugs = client.get_bugs()
        summary = summarize_bugs(bugs)
        if summary:
            log.info("\n📋 Bug Summary:\n" + summary)
        else:
            log.warning("Could not generate summary (check OPENAI_API_KEY)")
    
    elif task == "sprint" and item_ids:
        ids = [int(id.strip()) for id in item_ids.split(",")]
        items = client.get_work_items(ids)
        summary = summarize_sprint(items)
        if summary:
            log.info("\n📊 Sprint Summary:\n" + summary)
    
    elif task == "pipeline" and item_ids:
        from tasks.pipeline_checks import analyze_build_failure
        from clients.devops_client import DevOpsClient
        
        client = DevOpsClient()
        build_id = int(item_ids)
        build_info = client.get_build_summary(build_id)
        analysis = analyze_build_failure(build_info)
        
        # Get logs for deeper analysis
        logs = client.get_build_logs(build_id)
        
        summary = summarize_pipeline_failure(analysis, logs)
        if summary:
            log.info("\n🔍 Pipeline Failure Analysis:\n" + summary)


def run_rate(item_id: Optional[int] = None):
    """Rate work item priority using LLM."""
    from clients.devops_client import DevOpsClient
    
    if not item_id:
        log.error("--id required for rate task")
        return
    
    client = DevOpsClient()
    items = client.get_work_items([item_id])
    
    if not items:
        log.error(f"Work item #{item_id} not found")
        return
    
    result = rate_work_item_priority(items[0])
    
    if result:
        log.info(f"\n🎯 Priority Rating for #{item_id}:")
        if result.get("priority_score"):
            log.info(f"   Score: {result['priority_score']}/10")
        log.info(f"   Reasoning: {result.get('reasoning', 'N/A')}")
        log.info(f"   Recommendation: {result.get('recommendation', 'N/A')}")
        if result.get("factors"):
            log.info(f"   Factors: {', '.join(result['factors'])}")
    else:
        log.warning("Could not rate item (check OPENAI_API_KEY)")


def main():
    parser = argparse.ArgumentParser(
        description="DevOps Bot - Azure DevOps automation and AI assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s health                    List projects and health status
  %(prog)s bugs                      List active bugs with optional summary
  %(prog)s stale --days 7             Find items not updated in 7 days
  %(prog)s pipeline --hours 48       Check for failures in last 48 hours
  %(prog)s summarize bugs             LLM summary of active bugs
  %(prog)s rate --id 123             LLM priority rating for work item
        """
    )
    
    subparsers = parser.add_subparsers(dest="task", help="Task to run")

    # health command
    subparsers.add_parser("health", help="Run health checks")

    # bugs command
    bugs_parser = subparsers.add_parser("bugs", help="List active bugs")
    bugs_parser.add_argument("--no-summary", action="store_true", help="Skip LLM summary")

    # stale command
    stale_parser = subparsers.add_parser("stale", help="Find stale work items")
    stale_parser.add_argument("--days", type=int, default=14, help="Days threshold (default: 14)")
    stale_parser.add_argument("--project", type=str, help="Project override")
    stale_parser.add_argument("--notify", action="store_true", help="Send to Slack")

    # pipeline command
    pipe_parser = subparsers.add_parser("pipeline", help="Check pipeline failures")
    pipe_parser.add_argument("--hours", type=int, default=24, help="Hours to look back (default: 24)")
    pipe_parser.add_argument("--project", type=str, help="Project override")
    pipe_parser.add_argument("--notify", action="store_true", help="Send to Slack")

    # summarize command
    sum_parser = subparsers.add_parser("summarize", help="LLM summarization")
    sum_parser.add_argument("type", choices=["bugs", "sprint", "pipeline"], help="What to summarize")
    sum_parser.add_argument("--ids", help="Comma-separated item IDs (for sprint/pipeline)")

    # rate command
    rate_parser = subparsers.add_parser("rate", help="Rate work item priority")
    rate_parser.add_argument("--id", type=int, help="Work item ID to rate")

    # advice command (legacy)
    advice_parser = subparsers.add_parser("advice", help="Get AI advice")
    advice_parser.add_argument("--text", required=True, help="Question or context")

    args = parser.parse_args()

    if not args.task:
        parser.print_help()
        return

    try:
        if args.task == "health":
            run_health_checks()
        
        elif args.task == "bugs":
            run_bugs()
        
        elif args.task == "stale":
            run_stale(days=args.days, project=args.project, notify=args.notify)
        
        elif args.task == "pipeline":
            run_pipeline(hours=args.hours, project=args.project, notify=args.notify)
        
        elif args.task == "summarize":
            run_summarize(args.type, args.ids)
        
        elif args.task == "rate":
            run_rate(args.id)
        
        elif args.task == "advice":
            _run_advice(args.text)
        
        else:
            log.error(f"Unknown task: {args.task}")
    
    except KeyboardInterrupt:
        log.info("Interrupted by user")
    except Exception as e:
        log.error(f"Task failed: {e}")
        raise


def _run_advice(text: str):
    """Run advice task with optional OpenAI API."""
    from config import OPENAI_API_KEY
    from llm.advisor import get_advice

    if not OPENAI_API_KEY:
        log.warning("OPENAI_API_KEY not set. Skipping advice task.")
        log.info("Set OPENAI_API_KEY in .env to enable AI advice.")
        return

    log.info("Getting advice...")
    result = get_advice(text)
    log.info(f"Advice: {result}")


if __name__ == "__main__":
    main()
