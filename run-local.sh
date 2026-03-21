docker build -t devops-bot .
docker run --env-file .env devops-bot health