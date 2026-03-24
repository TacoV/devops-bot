"""
Slack notification support for DevOps bot alerts.
"""
import json
from typing import Optional, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from config import SLACK_WEBHOOK_URL
from utils.logger import get_logger

log = get_logger()

HAS_SLACK = bool(SLACK_WEBHOOK_URL)


def _send_to_slack(payload: dict) -> bool:
    """Send a payload to Slack webhook."""
    if not HAS_SLACK:
        log.debug("Slack webhook not configured, skipping notification")
        return False
    
    try:
        data = json.dumps(payload).encode("utf-8")
        request = Request(
            SLACK_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urlopen(request, timeout=10) as response:
            return response.status == 200
    except HTTPError as e:
        log.error(f"Slack webhook error: {e.code} - {e.reason}")
        return False
    except URLError as e:
        log.error(f"Slack connection error: {e.reason}")
        return False
    except Exception as e:
        log.error(f"Slack notification failed: {e}")
        return False


def send_message(text: str, channel: Optional[str] = None) -> bool:
    """
    Send a simple text message to Slack.
    
    Args:
        text: Message text (supports Slack markdown)
        channel: Optional channel override
    
    Returns:
        True if sent successfully
    """
    payload = {"text": text}
    if channel:
        payload["channel"] = channel
    
    return _send_to_slack(payload)


def send_block_message(blocks: list[dict], text: str = "", channel: Optional[str] = None) -> bool:
    """
    Send a rich block message to Slack.
    
    Args:
        blocks: Slack Block Kit blocks
        text: Fallback text for notifications
        channel: Optional channel override
    
    Returns:
        True if sent successfully
    """
    payload = {"blocks": blocks}
    if text:
        payload["text"] = text
    if channel:
        payload["channel"] = channel
    
    return _send_to_slack(payload)


def format_bug_alert(bugs: list[dict]) -> bool:
    """Send an alert about active bugs to Slack."""
    if not bugs:
        return True
    
    # Limit to first 10 for readability
    display_bugs = bugs[:10]
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🐛 Active Bugs: {len(bugs)} total",
                "emoji": True
            }
        },
        {"type": "divider"}
    ]
    
    for bug in display_bugs:
        fields = bug.get("fields", {})
        title = fields.get("System.Title", "No title")[:100]
        state = fields.get("System.State", "Unknown")
        priority = fields.get("System.Priority", "?")
        
        if isinstance(fields.get("System.AssignedTo"), dict):
            assigned = fields.get("System.AssignedTo", {}).get("displayName", "Unassigned")
        else:
            assigned = fields.get("System.AssignedTo", "Unassigned")
        
        priority_emoji = {
            1: "🔴",
            2: "🟠", 
            3: "🟡",
            4: "🔵"
        }.get(priority, "⚪")
        
        blocks.append({
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*#{bug['id']}* {priority_emoji}"},
                {"type": "mrkdwn", "text": f"State: {state}"},
                {"type": "mrkdwn", "text": f"*{title}*"},
                {"type": "mrkdwn", "text": f"Assigned: {assigned}"}
            ]
        })
    
    if len(bugs) > 10:
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"_...and {len(bugs) - 10} more_"}
            ]
        })
    
    return send_block_message(blocks, f"Active bugs: {len(bugs)}")


def format_pipeline_alert(failed_builds: list[dict]) -> bool:
    """Send an alert about failed pipelines to Slack."""
    if not failed_builds:
        return send_message("✅ *No recent pipeline failures!*")
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔴 Pipeline Failures: {len(failed_builds)} build(s)",
                "emoji": True
            }
        },
        {"type": "divider"}
    ]
    
    # Group by pipeline
    by_pipeline = {}
    for build in failed_builds:
        name = build.get("definition_name", "Unknown")
        if name not in by_pipeline:
            by_pipeline[name] = []
        by_pipeline[name].append(build)
    
    for pipeline, builds in list(by_pipeline.items())[:5]:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*📁 {pipeline}* ({len(builds)} failure(s))"}
        })
        
        for build in builds[:3]:
            url = build.get("url", "#")
            branch = build.get("source_branch", "unknown")
            requested = build.get("requested_by", "unknown")
            blocks.append({
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"`<{url}|#{build['build_number']}>` • {branch} • by {requested}"}
                ]
            })
    
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": "Investigate failures to prevent blocking the team."}
        ]
    })
    
    return send_block_message(
        blocks, 
        f"Pipeline failures: {len(failed_builds)} across {len(by_pipeline)} pipeline(s)"
    )


def format_stale_items_alert(stale_items: list[dict], days: int = 14) -> bool:
    """Send an alert about stale work items to Slack."""
    if not stale_items:
        return True
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"⏰ Stale Items: {len(stale_items)} item(s) not updated in {days}+ days",
                "emoji": True
            }
        },
        {"type": "divider"}
    ]
    
    for item in stale_items[:10]:
        fields = item.get("fields", {})
        title = fields.get("System.Title", "No title")[:80]
        work_type = fields.get("System.WorkItemType", "Task")
        state = fields.get("System.State", "Unknown")
        changed = fields.get("System.ChangedDate", "Unknown")
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{work_type}* #{item['id']}: {title}\n_State: {state} • Last updated: {changed[:10]}_"
            }
        })
    
    if len(stale_items) > 10:
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"_...and {len(stale_items) - 10} more items_"}
            ]
        })
    
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": "Consider updating or closing these items."}
        ]
    })
    
    return send_block_message(
        blocks,
        f"Stale items alert: {len(stale_items)} items not updated in {days}+ days"
    )


def format_sprint_summary(work_items: list[dict], sprint_name: str = "Sprint Summary") -> bool:
    """Send a sprint summary to Slack."""
    if not work_items:
        return send_message("No work items to summarize for this sprint.")
    
    # Count by state
    by_state = {}
    for item in work_items:
        state = item.get("fields", {}).get("System.State", "Unknown")
        by_state[state] = by_state.get(state, 0) + 1
    
    state_icons = {
        "Closed": "✅",
        "Completed": "✅",
        "Done": "✅",
        "Active": "🔄",
        "In Progress": "🔄",
        "New": "📋",
        "To Do": "📋",
        "Open": "📋"
    }
    
    stats = "\n".join([
        f"{state_icons.get(state, '•')} {state}: {count}"
        for state, count in sorted(by_state.items())
    ])
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 {sprint_name}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Total items: {len(work_items)}*\n\n{stats}"}
        }
    ]
    
    return send_block_message(blocks, f"Sprint Summary: {len(work_items)} items")
