"""
Team configuration for DevOps bot rules and conventions.

Teams customize this file to match their workflow:
- Work item types and states
- State transitions
- Sprint patterns
- Priority thresholds
- Stale item thresholds
"""
from typing import Optional


class TeamConfig:
    """Configuration for a specific team's DevOps workflow."""
    
    # === Project Settings ===
    project: str = "YourProject"
    project_id: str = "your-project-guid"
    
    # === Work Item Types ===
    # Which types exist in your project
    work_item_types: list[str] = ["Bug", "Task", "User Story", "Epic", "Feature"]
    
    # === States ===
    # Valid states per work item type
    states_by_type: dict[str, list[str]] = {
        "Bug": ["New", "Active", "Approved", "Committed", "Done", "Closed"],
        "Task": ["To Do", "In Progress", "Done"],
        "User Story": ["New", "Active", "Done", "Closed"],
        "Epic": ["New", "In Progress", "Done"],
        "Feature": ["New", "Ready", "In Progress", "Done"],
    }
    
    # States that count as "completed" or "done"
    completed_states: list[str] = ["Done", "Closed"]
    
    # States that count as "active" or "in progress"
    active_states: list[str] = ["Active", "In Progress", "Committed"]
    
    # === State Transitions ===
    # Which states can transition to which (for auto-fix suggestions)
    valid_transitions: dict[str, list[str]] = {
        "New": ["Active", "Closed"],
        "Active": ["Done", "Closed"],
        "Approved": ["Committed"],
        "Committed": ["Done"],
        "Done": ["Closed"],
    }
    
    # === Sprint/Iteration Settings ===
    # Pattern for sprint names (e.g., "Sprint 2024-01" or "Sprint 42")
    sprint_name_pattern: str = r"Sprint \d+"
    
    # Default sprint duration in weeks
    sprint_duration_weeks: int = 2
    
    # === Priority Thresholds ===
    # Priority values 1-4 in Azure DevOps
    critical_priority: int = 1
    high_priority: int = 2
    medium_priority: int = 3
    low_priority: int = 4
    
    # === Stale Item Thresholds ===
    # Days before an item is considered stale (by state)
    stale_threshold_days: dict[str, int] = {
        "New": 7,
        "Active": 14,
        "In Progress": 21,
        "Done": 30,  # Done but not closed
    }
    
    # Default stale threshold for unknown states
    default_stale_days: int = 14
    
    # === Hierarchy Rules ===
    # Allowed parent-child type relationships
    hierarchy_rules: dict[str, list[str]] = {
        "Epic": ["Feature", "User Story", "Task"],
        "Feature": ["User Story", "Task"],
        "User Story": ["Task"],
        "Bug": ["Task"],  # Bugs can have tasks
        "Task": [],  # Tasks are leaves
    }
    
    # Work item types that should always have a parent
    require_parent: list[str] = ["Task", "Bug"]
    
    # Work item types that should never have a parent (root items)
    root_types: list[str] = ["Epic"]
    
    # === Duplicates Detection ===
    # Fields to compare for duplicate detection
    duplicate_check_fields: list[str] = [
        "System.Title",
        "System.Description",
        "System.Tags",
    ]
    
    # Similarity threshold for duplicate detection (0.0 - 1.0)
    duplicate_similarity_threshold: float = 0.8
    
    # === Auto-Fix Settings ===
    # Enable/disable auto-fix suggestions
    auto_close_duplicates: bool = False
    auto_close_old_done: bool = True  # Close Done items older than X days
    auto_close_done_days: int = 30
    
    # === LLM Settings ===
    # System prompt for LLM advice (team-specific context)
    llm_system_context: str = """You are a DevOps assistant for a team using Azure DevOps.
Be practical, concise, and focused on actionable advice.
Consider the team's workflow and conventions."""
    
    # === Custom WIQL Helpers ===
    # Build a WIQL query for active work items of a type
    def active_items_query(self, work_item_type: str) -> str:
        states = self.states_by_type.get(work_item_type, [])
        # Exclude completed states
        open_states = [s for s in states if s not in self.completed_states]
        states_str = ", ".join(f"'{s}'" for s in open_states)
        
        return f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType],
                   [System.AssignedTo], [System.ChangedDate], [System.Priority]
            FROM WorkItems
            WHERE
                [System.TeamProject] = '{self.project}'
                AND [System.WorkItemType] = '{work_item_type}'
                AND [System.State] IN ({states_str})
            ORDER BY [System.Priority], [System.ChangedDate]
        """
    
    # Build a WIQL query for stale items
    def stale_items_query(self, work_item_type: Optional[str] = None, days: Optional[int] = None) -> str:
        type_filter = ""
        if work_item_type:
            type_filter = f"AND [System.WorkItemType] = '{work_item_type}'"
        
        stale_days = days or self.default_stale_days
        
        return f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType],
                   [System.AssignedTo], [System.ChangedDate], [System.CreatedDate], [System.Priority]
            FROM WorkItems
            WHERE
                [System.TeamProject] = '{self.project}'
                {type_filter}
                AND [System.ChangedDate] < @today - {stale_days}
            ORDER BY [System.ChangedDate}
        """
    
    # Check if a state transition is valid
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        valid_next_states = self.valid_transitions.get(from_state, [])
        return to_state in valid_next_states


# Default instance - teams copy this and customize
default_team = TeamConfig()
