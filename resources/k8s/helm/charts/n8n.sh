#!/bin/bash

# Set variables
REPO_URL="https://github.com/8gears/n8n-helm-chart.git"
BRANCH="0.25.2"
REPO_DIR="n8n-helm-chart"
CHART_PATH="charts/n8n"
PACKAGE_NAME="n8n-0.25.2.tgz"

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

# Add Bitnami repository for Redis dependency
echo "Adding Bitnami Helm repository..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Update dependencies
echo "Updating chart dependencies..."
helm dependency update

if [ $? -ne 0 ]; then
    echo "Error: Failed to update dependencies"
    exit 1
fi

# Package the chart
echo "Packaging Helm chart..."
helm package . -d ../../.. --version 0.25.2

if [ $? -ne 0 ]; then
    echo "Error: Failed to package Helm chart"
    exit 1
fi

echo "Successfully packaged chart to $(realpath ../../../$PACKAGE_NAME)"

# Clean up
echo "Cleaning up..."
cd -
rm -rf $REPO_DIR

echo "Done."
