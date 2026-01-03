#!/bin/bash

# Script to clean up incomplete multipart uploads on Cloudflare R2
# Usage: ./cleanup_r2_multipart.sh
#
# Required environment variables:
#   AWS_ACCESS_KEY_ID - R2 Access Key ID
#   AWS_SECRET_ACCESS_KEY - R2 Secret Access Key
#   R2_ENDPOINT - R2 endpoint URL (e.g., https://ACCOUNT_ID.r2.cloudflarestorage.com)
#   BUCKET_NAME - R2 bucket name (default: tqtensor-homelab)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check required environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo -e "${RED}Error: AWS_ACCESS_KEY_ID is not set${NC}"
    exit 1
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${RED}Error: AWS_SECRET_ACCESS_KEY is not set${NC}"
    exit 1
fi

if [ -z "$R2_ENDPOINT" ]; then
    echo -e "${RED}Error: R2_ENDPOINT is not set${NC}"
    exit 1
fi

# Default bucket name
BUCKET_NAME="${BUCKET_NAME:-tqtensor-homelab}"

echo -e "${GREEN}=== R2 Multipart Upload Cleanup ===${NC}"
echo "Bucket: ${BUCKET_NAME}"
echo "Endpoint: ${R2_ENDPOINT}"
echo ""

# List all incomplete multipart uploads
echo -e "${YELLOW}Scanning for incomplete multipart uploads...${NC}"
UPLOADS=$(aws s3api list-multipart-uploads \
    --bucket "${BUCKET_NAME}" \
    --endpoint-url "${R2_ENDPOINT}" \
    --output json 2>/dev/null || echo '{}')

# Check if there are any uploads
UPLOAD_COUNT=$(echo "$UPLOADS" | jq -r '.Uploads // [] | length')

if [ "$UPLOAD_COUNT" -eq 0 ]; then
    echo -e "${GREEN}No incomplete multipart uploads found. Nothing to clean up!${NC}"
    exit 0
fi

echo -e "${YELLOW}Found ${UPLOAD_COUNT} incomplete multipart upload(s)${NC}"
echo ""

# Display the uploads
echo "$UPLOADS" | jq -r '.Uploads[] | "Key: \(.Key)\nUpload ID: \(.UploadId)\nInitiated: \(.Initiated)\n"'

# Ask for confirmation
echo -e "${YELLOW}Do you want to abort all these incomplete multipart uploads? (yes/no)${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}Aborted by user${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Aborting incomplete multipart uploads...${NC}"

# Abort each upload
ABORTED=0
FAILED=0

while IFS= read -r line; do
    KEY=$(echo "$line" | jq -r '.Key')
    UPLOAD_ID=$(echo "$line" | jq -r '.UploadId')

    echo -n "Aborting: ${KEY} ... "

    if aws s3api abort-multipart-upload \
        --bucket "${BUCKET_NAME}" \
        --key "${KEY}" \
        --upload-id "${UPLOAD_ID}" \
        --endpoint-url "${R2_ENDPOINT}" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((ABORTED++))
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
    fi
done < <(echo "$UPLOADS" | jq -c '.Uploads[]')

echo ""
echo -e "${GREEN}=== Cleanup Summary ===${NC}"
echo "Successfully aborted: ${ABORTED}"
if [ "$FAILED" -gt 0 ]; then
    echo -e "${RED}Failed to abort: ${FAILED}${NC}"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
