"""
Configuration package for DevOps bot.
"""
from config.env import (
    DEVOPS_URL,
    DEVOPS_TOKEN,
    DEVOPS_PROJECT,
    DEVOPS_PROJECTID,
    OPENAI_API_KEY,
)
from config.team import TeamConfig, default_team

# Re-export all config
__all__ = [
    "DEVOPS_URL",
    "DEVOPS_TOKEN",
    "DEVOPS_PROJECT",
    "DEVOPS_PROJECTID",
    "OPENAI_API_KEY",
    "TeamConfig",
    "default_team",
]