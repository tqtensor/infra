#!/usr/bin/env python3
import os
import tempfile

from huggingface_hub import snapshot_download

# Check if MNT_DIR environment variable exists
if "MNT_DIR" not in os.environ:
    print("Error: MNT_DIR environment variable is not set")
    exit(1)

# Use a local temp directory for caching
cache_dir = tempfile.gettempdir()
print(f"Using cache directory: {cache_dir}")

try:
    model_path = snapshot_download(
        repo_id="google/flan-t5-base",
        ignore_patterns=["*.md"],
        local_dir=os.environ["MNT_DIR"],
        cache_dir=cache_dir,
    )
    print(f"Successfully downloaded model to {model_path}")
except Exception as error:
    print(f"Error downloading model: {error}")
    raise
