"""
LLM client supporting both Ollama (free, local) and OpenAI.
Uses Ollama by default - set OPENAI_API_KEY to use OpenAI instead.
"""
import json
from typing import Optional
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OPENAI_API_KEY
from utils.logger import get_logger

log = get_logger()

# Check what's available
HAS_OPENAI = bool(OPENAI_API_KEY)

# Try to import OpenAI
if HAS_OPENAI:
    try:
        from openai import OpenAI as OpenAIClient
        _openai_client = OpenAIClient(api_key=OPENAI_API_KEY)
    except ImportError:
        log.warning("OpenAI package not installed. Install with: pip install openai")
        HAS_OPENAI = False

# Check if Ollama is available
try:
    import urllib.request
    req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
    with urllib.request.urlopen(req, timeout=2) as response:
        HAS_OLLAMA = response.status == 200
except Exception:
    HAS_OLLAMA = False

log.info(f"LLM providers: Ollama={HAS_OLLAMA}, OpenAI={HAS_OPENAI}")


def _call_ollama(model: str, messages: list[dict], stream: bool = False) -> Optional[str]:
    """Call Ollama API (free, local)."""
    import urllib.request
    import urllib.error
    
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream
    }
    
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("message", {}).get("content")
    except urllib.error.URLError as e:
        log.error(f"Ollama connection failed: {e}")
        log.info("Make sure Ollama is running: https://ollama.ai/")
        return None
    except Exception as e:
        log.error(f"Ollama call failed: {e}")
        return None


def _call_openai(model: str, messages: list[dict]) -> Optional[str]:
    """Call OpenAI API (requires API key)."""
    if not HAS_OPENAI:
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
    model: Optional[str] = None,
    use_openai: bool = False
) -> Optional[str]:
    """
    Generate a completion using available LLM provider.
    
    Args:
        prompt: User message
        system_prompt: System context
        model: Model name (defaults to config value)
        use_openai: Force OpenAI even if Ollama is available
    
    Returns:
        Generated text or None if unavailable
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # Determine which provider to use
    if use_openai and HAS_OPENAI:
        model = model or "gpt-4o-mini"
        return _call_openai(model, messages)
    
    if HAS_OLLAMA:
        model = model or OLLAMA_MODEL
        return _call_ollama(model, messages)
    
    if HAS_OPENAI:
        model = model or "gpt-4o-mini"
        return _call_openai(model, messages)
    
    log.warning("No LLM provider available. Install Ollama or set OPENAI_API_KEY.")
    return None


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
        print("No LLM available. Install Ollama or set OPENAI_API_KEY.")
