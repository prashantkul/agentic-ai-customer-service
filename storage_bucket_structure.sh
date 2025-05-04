#!/bin/bash
# This script creates a Google Cloud Storage bucket and a specific folder structure within it.
# DO NOT execute this script again, the bucket and folders already exist.
gcloud storage buckets create gs://bettersale-product-images --location=us-central1 --uniform-bucket-level-access --enable-hierarchical-namespace

# Define the base GCS bucket path
GCS_BUCKET="gs://bettersale-product-images"

# Define the list of specific folder paths to create.
# The --recursive flag will create parent folders if they don't exist.
FOLDER_PATHS=(
    "basketball/apparel/"
    "basketball/equipment/"
    "basketball/footwear/"
    "cycling/accessories/"
    "cycling/apparel/"
    "cycling/equipment/"
    "cycling/safety/"
    "general/accessories/"
    "golf/accessories/"
    "golf/apparel/"
    "golf/equipment/"
    "golf/footwear/"
    "hiking/accessories/"
    "hiking/apparel/"
    "hiking/equipment/"
    "hiking/footwear/"
    "running/accessories/"
    "running/apparel/"
    "running/electronics/"
    "running/footwear/"
    "soccer/apparel/"
    "soccer/equipment/"
    "soccer/footwear/"
    "swimming/accessories/"
    "swimming/apparel/"
    "swimming/equipment/"
    "tennis/accessories/"
    "tennis/apparel/"
    "tennis/equipment/"
    "tennis/footwear/"
    "yoga/accessories/"
    "yoga/apparel/"
    "yoga/equipment/"
)

echo "Creating folder structure in ${GCS_BUCKET} using gcloud storage..."

# Loop through the list of paths and create each folder
for PATH_SUFFIX in "${FOLDER_PATHS[@]}"; do
    FULL_PATH="${GCS_BUCKET}/${PATH_SUFFIX}"
    echo "Creating folder: ${FULL_PATH}"
    gcloud storage folders create --recursive "${FULL_PATH}"

    # Optional: Add a check for command success
    if [ $? -ne 0 ]; then
        echo "Error creating folder: ${FULL_PATH}. Aborting."
        exit 1
    fi
done

echo ""
echo "All specified folders created successfully (or already existed)."