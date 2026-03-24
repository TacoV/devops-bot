"""
Configuration package for DevOps bot.

Usage:
    from config import team  # Team-specific settings
    from config import DEVOPS_URL, etc.  # Environment variables
"""
from config.team import TeamConfig, default_team

# Re-export team config
__all__ = ["TeamConfig", "default_team"]
