#!/bin/bash

# Check if AWS profile "personal" exists in credentials file
AWS_CREDENTIALS_FILE="$HOME/.aws/credentials"
PROFILE_NAME="personal"

if [ ! -f "$AWS_CREDENTIALS_FILE" ]; then
    echo "Error: AWS credentials file not found at $AWS_CREDENTIALS_FILE"
    exit 1
fi

# Check if profile exists
if grep -q "^\[${PROFILE_NAME}\]" "$AWS_CREDENTIALS_FILE"; then
    echo "AWS profile '${PROFILE_NAME}' found!"
    export AWS_PROFILE=$PROFILE_NAME
    echo "Exported AWS_PROFILE=${PROFILE_NAME}"
else
    echo "Error: AWS profile '${PROFILE_NAME}' not found in credentials file"
    exit 1
fi

# Login to Pulumi backend
echo ""
echo "Logging in to Pulumi backend..."
pulumi login "s3://pulumi-pixelml?region=us-east-1"

if [ $? -ne 0 ]; then
    echo "Error: Failed to login to Pulumi backend"
    exit 1
fi

echo "Successfully logged in to Pulumi backend!"

# Ask user which Pulumi command to run
echo ""
echo "Which Pulumi command would you like to run?"
echo "  u  - pulumi up"
echo "  r  - pulumi refresh"
echo "  ru - pulumi refresh -y && pulumi up"
echo ""
read -p "Enter your choice (u/r/ru): " choice

case "$choice" in
    u)
        echo "Running: pulumi up"
        pulumi up
        ;;
    r)
        echo "Running: pulumi refresh"
        pulumi refresh
        ;;
    ru)
        echo "Running: pulumi refresh -y && pulumi up"
        pulumi refresh -y && pulumi up
        ;;
    *)
        echo "Invalid choice. Please enter u, r, or ru"
        exit 1
        ;;
esac
