import os
from dotenv import load_dotenv

load_dotenv()

DEVOPS_URL = os.getenv("DEVOPS_URL")
DEVOPS_TOKEN = os.getenv("DEVOPS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")