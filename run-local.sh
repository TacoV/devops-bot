#!/bin/bash
# Run all tasks in succession for testing via Docker

set +e  # Continue on error so we can run all tasks

echo "=== Building Docker image ==="
docker build -t devops-bot .

echo ""
echo "=== Running health checks (Docker) ==="
docker run --env-file .env devops-bot health

echo ""
echo "=== Listing bugs (Docker) ==="
docker run --env-file .env devops-bot bugs

echo ""
echo "=== Getting advice (Docker) ==="
echo "Note: This will be skipped if OPENAI_API_KEY is not set"
docker run --env-file .env devops-bot advice --text "How do I improve my DevOps pipeline?"
