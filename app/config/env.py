import os

from dotenv import load_dotenv
load_dotenv()

# Azure DevOps Configuration
DEVOPS_URL = os.getenv("DEVOPS_URL")
DEVOPS_TOKEN = os.getenv("DEVOPS_TOKEN")
DEVOPS_PROJECT = os.getenv("DEVOPS_PROJECT")
DEVOPS_PROJECTID = os.getenv("DEVOPS_PROJECTID")
