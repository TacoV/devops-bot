import argparse
from tasks.health_checks import run_health_checks
from tasks.list_bugs import list_bugs
from utils.logger import get_logger

log = get_logger()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="Task to run: health, bugs, or advice")
    parser.add_argument("--text", help="Text for advice task")
    args = parser.parse_args()

    if args.task == "health":
        log.info("Running health checks...")
        run_health_checks()
    elif args.task == "bugs":
        log.info("Listing bugs...")
        list_bugs()
    elif args.task == "advice":
        _run_advice(args.text)
    else:
        log.error(f"Unknown task: {args.task}")


def _run_advice(text):
    """Run advice task with optional OpenAI API."""
    from config import OPENAI_API_KEY
    from llm.advisor import get_advice

    if not OPENAI_API_KEY:
        log.warning("OPENAI_API_KEY not set. Skipping advice task.")
        log.info("Set OPENAI_API_KEY in .env to enable AI advice.")
        return

    if not text:
        log.error("Missing --text argument for advice task")
        return

    log.info("Getting advice...")
    result = get_advice(text)
    log.info(f"Advice: {result}")

if __name__ == "__main__":
    main()