import argparse
from tasks.health_checks import run_health_checks
from tasks.list_bugs import list_bugs
from llm.advisor import get_advice
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
        if not args.text:
            log.error("Missing --text argument for advice task")
            return
        log.info("Getting advice...")
        result = get_advice(args.text)
        log.info(f"Advice: {result}")
    else:
        log.error(f"Unknown task: {args.task}")

if __name__ == "__main__":
    main()