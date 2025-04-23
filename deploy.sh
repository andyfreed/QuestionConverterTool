#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set your Digital Ocean App Platform information
APP_NAME="question-converter-tool"

echo "Building Docker image..."
docker build -t ${APP_NAME}:latest .

echo "Logging in to Digital Ocean Container Registry..."
# You'll need to create a personal access token in Digital Ocean and use it here
# doctl auth init -t <your-personal-access-token>

echo "Tagging the Docker image for Digital Ocean..."
# Replace 'registry.digitalocean.com/your-registry-name' with your actual registry URL
# docker tag ${APP_NAME}:latest registry.digitalocean.com/your-registry-name/${APP_NAME}:latest

echo "Pushing the Docker image to Digital Ocean..."
# docker push registry.digitalocean.com/your-registry-name/${APP_NAME}:latest

echo "Deploying to Digital Ocean App Platform..."
# If using doctl (Digital Ocean CLI tool):
# doctl apps create --spec app-spec.yaml
# OR to update an existing app:
# doctl apps update <app-id> --spec app-spec.yaml

echo "Deployment completed!" 