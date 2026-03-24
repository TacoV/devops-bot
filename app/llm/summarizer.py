"""
LLM-powered summarization for DevOps work items and reports.
Uses Ollama (free, local) by default, OpenAI as fallback.
"""
from typing import Optional
from llm.client import complete, complete_json
from utils.logger import get_logger

log = get_logger()


def summarize_bugs(bugs: list[dict], include_priority: bool = True) -> Optional[str]:
    """
    Summarize a list of bug work items into a concise report.
    
    Args:
        bugs: List of bug work items with fields
        include_priority: Whether to mention priority levels
    
    Returns:
        LLM-generated summary or None if LLM unavailable
    """
    if not bugs:
        return "No bugs to summarize."
    
    # Build context from bugs
    bug_list = []
    for bug in bugs[:10]:  # Limit to 10 for context length
        fields = bug.get("fields", {})
        title = fields.get("System.Title", "No title")
        state = fields.get("System.State", "Unknown")
        assigned = fields.get("System.AssignedTo", "Unassigned")
        priority = fields.get("System.Priority", "Not set")
        
        if isinstance(assigned, dict):
            assigned = assigned.get("displayName", "Unassigned")
        
        item = f"- #{bug['id']}: {title} (State: {state}, Assigned: {assigned}"
        if include_priority:
            item += f", Priority: {priority}"
        item += ")"
        bug_list.append(item)
    
    bugs_text = "\n".join(bug_list)
    count_note = f" (showing first 10 of {len(bugs)})" if len(bugs) > 10 else ""
    
    system_prompt = """You are a DevOps assistant that summarizes bug reports.
Keep summaries concise, actionable, and technical.
Group related bugs when possible.
Highlight any patterns or common root causes.
Format with bullet points and headers."""
    
    user_content = f"""Summarize these {len(bugs)} active bug(s){count_note}:

{bugs_text}

Provide:
1. Brief overview of the bug landscape
2. Key themes or patterns (if any)
3. Most urgent items needing attention
4. Suggested prioritization"""

    return complete(user_content, system_prompt)


def summarize_sprint(work_items: list[dict], sprint_name: str = "current sprint") -> Optional[str]:
    """
    Generate a sprint summary from work items.
    
    Args:
        work_items: List of work items in the sprint
        sprint_name: Name/identifier for the sprint
    
    Returns:
        LLM-generated sprint summary
    """
    if not work_items:
        return "No work items to summarize."
    
    # Categorize by state
    by_state = {}
    for item in work_items:
        state = item.get("fields", {}).get("System.State", "Unknown")
        if state not in by_state:
            by_state[state] = []
        by_state[state].append(item)
    
    # Build summary context
    categories = []
    for state, items in by_state.items():
        items_text = "\n".join([
            f"- #{i['id']}: {i.get('fields', {}).get('System.Title', 'No title')}"
            for i in items[:5]
        ])
        if len(items) > 5:
            items_text += f"\n- ... and {len(items) - 5} more"
        categories.append(f"### {state} ({len(items)} items)\n{items_text}")
    
    content = "\n\n".join(categories)
    
    system_prompt = """You are a DevOps assistant creating sprint summaries.
Be concise but informative.
Highlight completion status, blockers, and key achievements.
Format with markdown headers and bullet points."""
    
    user_content = f"""Generate a summary for the {sprint_name} based on these work items:

{content}

Include:
1. Sprint overview with completion metrics
2. Key deliverables
3. Any blockers or concerns
4. Team highlights"""

    return complete(user_content, system_prompt)


def condense_description(description: str, max_length: int = 200) -> Optional[str]:
    """
    Condense a lengthy work item description into a concise summary.
    
    Args:
        description: Original long description
        max_length: Target length for condensed version
    
    Returns:
        Condensed description
    """
    if not description or len(description) <= max_length:
        return description
    
    system_prompt = """You are a DevOps assistant summarizing work item descriptions.
Create a concise, technical summary that preserves key information.
Focus on: what needs to be done, why it matters, and any constraints.
Output only the condensed text, no preamble."""
    
    return complete(description, system_prompt)
