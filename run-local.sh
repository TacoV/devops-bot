#!/bin/bash
# Run all tasks in succession for testing via Docker

set +e  # Continue on error so we can run all tasks

echo "=== Building Docker image ==="
docker build -t devops-bot .

echo ""
echo "=== Running health checks (Docker) ==="
docker run --env-file .env devops-bot check
