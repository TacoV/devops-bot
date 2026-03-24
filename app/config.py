import os
from dotenv import load_dotenv

load_dotenv()

# Azure DevOps Configuration
DEVOPS_URL = os.getenv("DEVOPS_URL")
DEVOPS_TOKEN = os.getenv("DEVOPS_TOKEN")
DEVOPS_PROJECT = os.getenv("DEVOPS_PROJECT")
DEVOPS_PROJECTID = os.getenv("DEVOPS_PROJECTID")

# LLM Configuration (using Ollama for free local models)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")  # Default free model
# Set OPENAI_API_KEY if you want to use OpenAI instead
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
