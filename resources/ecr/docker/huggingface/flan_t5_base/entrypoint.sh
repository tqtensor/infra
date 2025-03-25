#!/usr/bin/env bash
set -eo pipefail

# Create mount directory for service
mkdir -p $MNT_DIR

echo "Mounting GCS Fuse."
gcsfuse --debug_gcs --debug_fuse $BUCKET $MNT_DIR
echo "Mounting completed."

# Create directory for Hugging Face
mkdir -p $MNT_DIR/hf

# Export needed environment variables
export HF_HOME=$MNT_DIR/hf
export HF_HUB_ENABLE_HF_TRANSFER=1
export SAFETENSORS_FAST_GPU=1
export BITSANDBYTES_NOWELCOME=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_NO_CACHE_DIR=1

# Download model weights
echo "Downloading from HuggingFace Hub."
$APP_HOME/download.sh
echo "Downloading completed."

# Run the web service
python3 $APP_HOME/main.py
