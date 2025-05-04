# BetterSale Customer Service - Deployment Guide

This document provides instructions for deploying the BetterSale Customer Service application using Docker and Google Cloud Run.

## Prerequisites

- Docker installed locally
- Google Cloud SDK (gcloud) installed and configured
- Access to a Google Cloud project

## Local Development with Docker

### Building and Running Locally

1. Build and start the application using Docker Compose:

```bash
docker-compose up --build
```

2. Access the Streamlit app at http://localhost:8501

3. To stop the application:

```bash
docker-compose down
```

## Deploying to Google Cloud Run

### Automatic Deployment

Use the included deployment script:

```bash
./deploy_to_cloud_run.sh
```

This script will:
1. Build the Docker image
2. Push it to Google Container Registry
3. Deploy it to Cloud Run
4. Output the URL for the deployed service

### Manual Deployment

If you prefer to deploy manually:

1. Build the Docker image:

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/bettersale-customer-service .
```

2. Push the image to Google Container Registry:

```bash
docker push gcr.io/YOUR_PROJECT_ID/bettersale-customer-service
```

3. Deploy to Cloud Run:

```bash
gcloud run deploy bettersale-customer-service \
  --image gcr.io/YOUR_PROJECT_ID/bettersale-customer-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="AGENT_BASE_URL=https://customer-service-agent-190206934161.us-central1.run.app,AGENT_APP_NAME=customer-service-agent-app"
```

## Environment Variables

The application uses the following environment variables:

- `AGENT_BASE_URL`: URL of the agent service (default: https://customer-service-agent-190206934161.us-central1.run.app)
- `AGENT_APP_NAME`: Name of the agent app (default: customer-service-agent-app)

You can override these values when deploying to Cloud Run using the `--set-env-vars` flag.

## Database Persistence

The SQLite database is contained in the `customer_service/database/` directory. For local development, this directory is mounted as a volume to persist data between container restarts.

For production deployments, consider using a more robust database solution like Cloud SQL instead of the embedded SQLite database.