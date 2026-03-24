"""
DevOps Bot - Azure DevOps automation and LLM-assisted tasks.
"""
import argparse
from typing import Optional

from utils.logger import get_logger
from llm.summarizer import summarize_bugs, summarize_sprint
from llm.reviewer import rate_work_item_priority

log = get_logger()


def run_health_checks():
    """Run basic health checks against Azure DevOps."""
    from clients.devops_client import DevOpsClient
    
    client = DevOpsClient()
    projects = client.get_projects()
    log.info(f"Found {projects.get('count', 0)} projects")
    
    for project in projects.get('value', [])[:5]:
        log.info(f"  - {project.get('name')}")
    
    if projects.get('count', 0) > 5:
        log.info(f"  ... and {projects.get('count', 0) - 5} more")


def run_bugs():
    """List and optionally summarize active bugs."""
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
    
    # Generate LLM summary if API key available
    if bugs:
        summary = summarize_bugs(bugs)
        if summary:
            log.info("\n📋 Bug Summary:\n" + summary)


def run_stale(days: int = 14, project: Optional[str] = None):
    """Find and report stale work items."""
    from tasks.stale_items import run_stale_check
    
    items = run_stale_check(days=days, project=project)
    return items


def run_summarize(task: str, item_ids: Optional[str] = None):
    """Summarize work items using LLM."""
    from clients.devops_client import DevOpsClient
    
    client = DevOpsClient()
    
    if task == "bugs":
        bugs = client.get_bugs()
        summary = summarize_bugs(bugs)
        if summary:
            log.info("\n📋 Bug Summary:\n" + summary)
        else:
            log.warning("Could not generate summary (check LLM configuration)")
    
    elif task == "sprint" and item_ids:
        ids = [int(id.strip()) for id in item_ids.split(",")]
        items = client.get_work_items(ids)
        summary = summarize_sprint(items)
        if summary:
            log.info("\n📊 Sprint Summary:\n" + summary)


def run_check():
    """Run work item consistency checks."""
    from tasks.consistency_checks import run_consistency_checks
    
    results = run_consistency_checks()
    return results


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
        log.warning("Could not rate item (check LLM configuration)")


def main():
    parser = argparse.ArgumentParser(
        description="DevOps Bot - Azure DevOps automation and AI assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s health                    List projects and health status
  %(prog)s bugs                      List active bugs with optional summary
  %(prog)s stale --days 7            Find items not updated in 7 days
  %(prog)s check                     Run consistency checks
  %(prog)s summarize bugs            LLM summary of active bugs
  %(prog)s rate --id 123             LLM priority rating for work item
        """
    )
    
    subparsers = parser.add_subparsers(dest="task", help="Task to run")

    # health command
    subparsers.add_parser("health", help="Run health checks")

    # bugs command
    bugs_parser = subparsers.add_parser("bugs", help="List active bugs")

    # stale command
    stale_parser = subparsers.add_parser("stale", help="Find stale work items")
    stale_parser.add_argument("--days", type=int, default=14, help="Days threshold (default: 14)")
    stale_parser.add_argument("--project", type=str, help="Project override")

    # summarize command
    sum_parser = subparsers.add_parser("summarize", help="LLM summarization")
    sum_parser.add_argument("type", choices=["bugs", "sprint"], help="What to summarize")
    sum_parser.add_argument("--ids", help="Comma-separated item IDs (for sprint)")

    # rate command
    rate_parser = subparsers.add_parser("rate", help="Rate work item priority")
    rate_parser.add_argument("--id", type=int, help="Work item ID to rate")

    # check command
    check_parser = subparsers.add_parser("check", help="Run consistency checks")
    check_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

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
            run_stale(days=args.days, project=args.project)
        
        elif args.task == "summarize":
            run_summarize(args.type, args.ids)
        
        elif args.task == "rate":
            run_rate(args.id)
        
        elif args.task == "check":
            run_check()
        
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
    """Run advice task with LLM."""
    from llm.advisor import get_advice
    from llm.client import HAS_OPENAI

    if not HAS_OPENAI:
        log.warning("No LLM provider available.")
        log.info("Set OPENAI_API_KEY to enable AI intelligence.")
        return

    log.info("Getting advice...")
    result = get_advice(text)
    log.info(f"Advice: {result}")


if __name__ == "__main__":
    main()
