#!/usr/bin/env python3
import os

from huggingface_hub import snapshot_download

# Check if MNT_DIR environment variable exists
if "MNT_DIR" not in os.environ:
    print("Error: MNT_DIR environment variable is not set")
    exit(1)

try:
    model_path = snapshot_download(
        repo_id="google/flan-t5-base",
        ignore_patterns=["*.md"],
        local_dir=os.environ["MNT_DIR"],
    )
    print(f"Successfully downloaded model to {model_path}")
except Exception as e:
    print(f"Error downloading model: {e}")
    raise
