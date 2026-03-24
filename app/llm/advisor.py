"""
LLM advisor for general DevOps questions.
Uses Ollama (free, local) by default, OpenAI as fallback.
"""
from llm.client import complete
from utils.logger import get_logger

log = get_logger()


def get_advice(text: str, model: str = None) -> str:
    """
    Get advice from LLM on any DevOps-related question.
    
    Args:
        text: The question or context to get advice on
        model: Optional model override
    
    Returns:
        LLM-generated advice
    """
    system_prompt = """You are a helpful DevOps assistant. Provide clear, actionable advice on:
- Azure DevOps and CI/CD pipelines
- Software development best practices
- Infrastructure and deployment
- Code review and quality
- Team collaboration

Be concise but thorough. When unsure, acknowledge limitations."""
    
    result = complete(text, system_prompt, model=model)
    
    if result:
        return result
    
    return "LLM unavailable. Please ensure Ollama is running or set OPENAI_API_KEY."
