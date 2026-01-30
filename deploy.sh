#!/bin/bash
# Deploy script for Creo Image Generator

# Set your values
# Load environment variables if .env exists
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

export BASE_URL="http://dify.yourads.io:8000"

# Build and run
docker compose up -d --build

echo "API running at http://dify.yourads.io:8000"
echo "Health check: curl http://dify.yourads.io:8000/health"
