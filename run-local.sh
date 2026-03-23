#!/bin/bash
# Run all tasks in succession for testing

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
docker run --env-file .env devops-bot advice --text "How do I improve my DevOps pipeline?"