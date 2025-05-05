#!/bin/bash
set -e

# Configuration
PROJECT_ID="privacy-ml-lab1"
SERVICE_NAME="bettersale-customer-service"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

cd "$(dirname "$0")"
gcloud config set project privacy-ml-lab1
echo "Current directory: $(pwd)"

# Option A: Build & push via Cloud Build (recommended)
echo "Building & pushing via Cloud Build (amd64)…"
gcloud builds submit --tag ${IMAGE_NAME} .

# --- If you really want a local fallback, uncomment below: ---
# echo "Local Buildx fallback: building & pushing linux/amd64…"
# docker buildx create --name multiarch-builder --use || true
# docker buildx build \
#   --builder multiarch-builder \
#   --platform linux/amd64 \
#   --tag ${IMAGE_NAME} \
#   --push \
#   .

# Deploy to Cloud Run
echo "Deploying to Cloud Run…"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars="AGENT_BASE_URL=https://customer-service-agent-190206934161.us-central1.run.app,AGENT_APP_NAME=customer-service-agent-app"

echo "Deployment complete! Service URL:"
gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(status.url)"