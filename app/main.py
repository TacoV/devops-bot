"""
DevOps Bot - Simple work item checks.
"""
import argparse
import importlib
import os
from pathlib import Path

from utils.logger import get_logger

log = get_logger()


def run_checks():
    """Run all checks from tasks/check directory."""
    checks_dir = Path(__file__).parent / "tasks" / "check"
    
    if not checks_dir.exists():
        log.error(f"Checks directory not found: {checks_dir}")
        return
    
    check_files = [
        f.stem for f in checks_dir.glob("*.py")
        if f.stem != "__init__" and not f.stem.startswith("_")
    ]
    
    if not check_files:
        log.warning("No check files found in tasks/check/")
        return
    
    log.info(f"Running {len(check_files)} check(s)...")
    
    for check_name in check_files:
        try:
            log.info(f"\n{'='*60}")
            log.info(f"Running check: {check_name}")
            log.info(f"{'='*60}")
            
            module = importlib.import_module(f"tasks.check.{check_name}")
            
            if hasattr(module, "run_check"):
                module.run_check()
            else:
                log.warning(f"Check '{check_name}' has no run_check() function")
        
        except Exception as e:
            log.error(f"Check '{check_name}' failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="DevOps Bot - Work item checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check                     Run all checks
        """
    )
    
    subparsers = parser.add_subparsers(dest="task", help="Task to run")
    
    # check command
    subparsers.add_parser("check", help="Run all checks")
    
    args = parser.parse_args()
    
    if not args.task:
        parser.print_help()
        return
    
    try:
        if args.task == "check":
            run_checks()
        else:
            log.error(f"Unknown task: {args.task}")
    
    except KeyboardInterrupt:
        log.info("Interrupted by user")
    except Exception as e:
        log.error(f"Task failed: {e}")
        raise


if __name__ == "__main__":
    main()
