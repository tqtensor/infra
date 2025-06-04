import argparse
import os

from huggingface_hub import snapshot_download

parser = argparse.ArgumentParser(
    description="Download a HuggingFace model snapshot to /data."
)
parser.add_argument(
    "--repo_id",
    type=str,
    default="Alibaba-NLP/gte-Qwen2-1.5B-instruct",
    help="HuggingFace repo ID to download",
)
args = parser.parse_args()

os.makedirs("/data", exist_ok=True)

snapshot_download(
    repo_id=args.repo_id,
    cache_dir="/data",
)

print(f"Downloaded {args.repo_id} to /data")
