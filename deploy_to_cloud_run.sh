#!/bin/bash
set -e

# Configuration
PROJECT_ID="privacy-ml-lab1"  # Replace with your Google Cloud project ID
SERVICE_NAME="bettersale-customer-service"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Build the Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

# Push the image to Google Container Registry
echo "Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars="AGENT_BASE_URL=https://customer-service-agent-190206934161.us-central1.run.app,AGENT_APP_NAME=customer-service-agent-app"

echo "Deployment complete! Your app should be available at:"
gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format="value(status.url)"