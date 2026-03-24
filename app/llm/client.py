"""
LLM client using OpenAI API with graceful fallback when no API key is provided.
"""
import json
from typing import Optional
from config import OPENAI_API_KEY
from utils.logger import get_logger

log = get_logger()

# Check if OpenAI is available
HAS_OPENAI = bool(OPENAI_API_KEY)

# Try to initialize OpenAI client
_openai_client = None
if HAS_OPENAI:
    try:
        from openai import OpenAI as OpenAIClient
        _openai_client = OpenAIClient(api_key=OPENAI_API_KEY)
    except ImportError:
        log.warning("OpenAI package not installed. Install with: pip install openai")
        HAS_OPENAI = False

if HAS_OPENAI:
    log.info("LLM: OpenAI enabled")
else:
    log.warning("LLM: No API key configured. Set OPENAI_API_KEY for AI intelligence.")


def _call_openai(model: str, messages: list[dict]) -> Optional[str]:
    """Call OpenAI API (requires API key)."""
    if not HAS_OPENAI or _openai_client is None:
        return None
    
    try:
        response = _openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        log.error(f"OpenAI call failed: {e}")
        return None


def complete(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    model: Optional[str] = None
) -> Optional[str]:
    """
    Generate a completion using OpenAI.
    
    Args:
        prompt: User message
        system_prompt: System context
        model: Model name (defaults to gpt-4o-mini)
    
    Returns:
        Generated text or None if unavailable
    """
    if not HAS_OPENAI:
        log.debug("LLM unavailable: No API key configured")
        return None
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    model = model or "gpt-4o-mini"
    return _call_openai(model, messages)


def complete_json(
    prompt: str,
    system_prompt: str = "You are a helpful assistant. Respond with valid JSON only.",
    model: Optional[str] = None
) -> Optional[dict]:
    """
    Generate JSON output from LLM.
    
    Returns:
        Parsed JSON dict or None
    """
    result = complete(prompt, system_prompt, model)
    
    if result:
        try:
            # Try to extract JSON from response
            text = result.strip()
            if text.startswith("```"):
                # Remove code blocks
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON: {e}")
    
    return None


# Example usage
if __name__ == "__main__":
    # Test the LLM
    result = complete("What is 2+2?")
    if result:
        print(f"LLM Response: {result}")
    else:
        print("No LLM available. Set OPENAI_API_KEY to enable AI intelligence.")
