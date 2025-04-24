#!/bin/bash

# Set variables
REPO_URL="https://github.com/BerriAI/litellm.git"
BRANCH="v1.67.0-stable"
REPO_DIR="litellm-helm-chart"
CHART_PATH="deploy/charts/litellm-helm"
PACKAGE_NAME="litellm-0.4.3.tgz"

# Clone the repository with specific branch
echo "Cloning repository from $REPO_URL (branch: $BRANCH)..."
git clone -b $BRANCH $REPO_URL $REPO_DIR

if [ $? -ne 0 ]; then
    echo "Error: Failed to clone repository"
    exit 1
fi

# Change to the chart directory
echo "Changing to chart directory: $REPO_DIR/$CHART_PATH"
cd "$REPO_DIR/$CHART_PATH" || {
    echo "Error: Failed to change directory"
    exit 1
}

# Package the chart
echo "Packaging Helm chart..."
helm package . -d ../../../.. --version 0.4.3

if [ $? -ne 0 ]; then
    echo "Error: Failed to package Helm chart"
    exit 1
fi

echo "Successfully packaged chart to $(realpath ../../../../$PACKAGE_NAME)"

# Clean up
echo "Cleaning up..."
cd -
rm -rf $REPO_DIR

echo "Done."
