"""
LLM-powered code and work item review/rating functionality.
Requires OPENAI_API_KEY to be set for AI intelligence.
"""
from typing import Optional
from llm.client import complete, complete_json
from utils.logger import get_logger

log = get_logger()


def rate_work_item_priority(work_item: dict) -> Optional[dict]:
    """
    Rate the priority/urgency of a work item using LLM analysis.
    
    Args:
        work_item: Work item with fields
    
    Returns:
        Dict with priority_score (1-10), reasoning, and recommendations
    """
    fields = work_item.get("fields", {})
    
    context = f"""Work Item #{work_item.get('id')}
Title: {fields.get('System.Title', 'No title')}
Type: {fields.get('System.WorkItemType', 'Unknown')}
State: {fields.get('System.State', 'Unknown')}
Description: {fields.get('System.Description', 'No description')}
Assigned to: {fields.get('System.AssignedTo', 'Unassigned')}
Tags: {fields.get('System.Tags', 'None')}
Current Priority: {fields.get('System.Priority', 'Not set')}
Created: {fields.get('System.CreatedDate', 'Unknown')}
Changed: {fields.get('System.ChangedDate', 'Unknown')}
"""
    
    system_prompt = """You are a DevOps priority analyst. Analyze work items and rate their urgency.
Consider: business impact, dependencies, age, stakeholder importance, and technical complexity.
Respond ONLY with valid JSON in this exact format:
{
    "priority_score": <number 1-10, 10 being most urgent>,
    "reasoning": "<2-3 sentence explanation>",
    "recommendation": "<specific action recommendation>",
    "factors": ["<factor1>", "<factor2>", ...]
}"""
    
    result = complete_json(context, system_prompt)
    
    return result


def review_code(
    code: str,
    language: Optional[str] = None,
    focus_areas: Optional[list[str]] = None
) -> Optional[str]:
    """
    Review code and provide improvement suggestions.
    
    Args:
        code: Code to review
        language: Programming language (auto-detected if not provided)
        focus_areas: Specific areas to focus on (e.g., ['security', 'performance'])
    
    Returns:
        LLM-generated code review
    """
    system_prompt = """You are a senior software engineer conducting code reviews.
Be thorough but constructive. Focus on:
- Code quality and readability
- Potential bugs and edge cases
- Security vulnerabilities
- Performance issues
- Best practices

Format with sections: Summary, Issues (with severity), Suggestions, Praise (for good parts)."""
    
    user_content = f"""Review this{language or ''} code:
```{language or ''}
{code}
```"""
    
    if focus_areas:
        user_content += f"\n\nFocus areas: {', '.join(focus_areas)}"
    
    return complete(user_content, system_prompt)


def assess_technical_debt(work_items: list[dict]) -> Optional[dict]:
    """
    Assess and prioritize technical debt items.
    
    Args:
        work_items: List of work items (tasks, bugs, etc.) related to tech debt
    
    Returns:
        Assessment with priority ranking and recommendations
    """
    if not work_items:
        return {"summary": "No tech debt items to assess.", "items": []}
    
    items_text = []
    for item in work_items[:20]:  # Limit context
        fields = item.get("fields", {})
        items_text.append(f"""#{item['id']}: {fields.get('System.Title', 'No title')}
State: {fields.get('System.State')}
Tags: {fields.get('System.Tags', 'None')}
Description: {fields.get('System.Description', 'No description')[:300]}...""")

    content = "\n\n---\n\n".join(items_text)
    count_note = f" (showing first 20 of {len(work_items)})" if len(work_items) > 20 else ""
    
    system_prompt = """You are a technical debt assessor. Analyze work items and rank tech debt by:
- Business impact
- Risk level
- Maintenance cost
- Dependencies

Respond ONLY with valid JSON:
{
    "summary": "<overall tech debt health assessment>",
    "priority_items": [
        {
            "id": <number>,
            "title": "<title>",
            "risk_level": "high/medium/low",
            "reasoning": "<why this is priority>"
        }
    ],
    "recommendations": ["<action1>", "<action2>"],
    "estimated_debt_score": <1-100>
}"""
    
    user_content = f"""Assess these {len(work_items)} tech debt items{count_note}:

{content}

Provide a prioritized assessment focusing on items that should be addressed first."""

    result = complete_json(user_content, system_prompt)
    
    return result


def suggest_acceptance_criteria(user_story: str) -> Optional[str]:
    """
    Generate acceptance criteria for a user story.
    
    Args:
        user_story: The user story text
    
    Returns:
        Suggested acceptance criteria
    """
    system_prompt = """You are a DevOps/Agile assistant that writes acceptance criteria.
Follow the Given-When-Then format or use clear bullet points.
Make criteria: specific, testable, measurable, and achievable.
Include both happy path and edge cases."""
    
    return complete(user_story, system_prompt)


def analyze_root_cause(bug_info: dict, related_items: Optional[list[dict]] = None) -> Optional[str]:
    """
    Help identify root causes of a bug.
    
    Args:
        bug_info: Bug work item details
        related_items: Potentially related bugs or incidents
    
    Returns:
        Root cause analysis
    """
    fields = bug_info.get("fields", {})
    
    context = f"""Bug #{bug_info.get('id')}
Title: {fields.get('System.Title', 'No title')}
Description: {fields.get('System.Description', 'No description')}
Steps to Reproduce: {fields.get('Microsoft.VSTS.TCM.ReproSteps', 'Not provided')}
System Info: {fields.get('Microsoft.VSTS.TCM.SystemInfo', 'Not provided')}
Assigned to: {fields.get('System.AssignedTo', 'Unassigned')}
Tags: {fields.get('System.Tags', 'None')}"""
    
    if related_items:
        context += "\n\n### Possibly Related Items\n"
        for item in related_items[:5]:
            item_fields = item.get("fields", {})
            context += f"- #{item['id']}: {item_fields.get('System.Title', 'No title')}\n"
    
    system_prompt = """You are a root cause analysis expert. Analyze bugs and identify underlying causes.
Consider: recent changes, dependencies, environmental factors, and patterns.
Provide structured analysis with evidence-based reasoning.
Suggest both immediate fixes and preventive measures."""
    
    user_content = f"""Analyze this bug and identify the likely root cause:

{context}

Provide:
1. Most likely root cause
2. Contributing factors
3. Evidence supporting this theory
4. Recommended investigation steps
5. Preventive measures"""

    return complete(user_content, system_prompt)
