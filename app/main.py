import argparse
from tasks.health_checks import run_health_checks
from tasks.list_bugs import list_bugs
from utils.logger import get_logger

log = get_logger()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="Task to run")
    args = parser.parse_args()

    if args.task == "health":
        # run_health_checks()
        list_bugs()
#    elif args.task == "cleanup-board":
#        cleanup_board()
    else:
        log.error(f"Unknown task: {args.task}")

if __name__ == "__main__":
    main()