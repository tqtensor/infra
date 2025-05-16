# NooBaa Setup Guide

NooBaa is an object storage service that provides S3-compatible API for Kubernetes applications.

## Prerequisites
- Kubernetes cluster up and running
- kubectl configured with appropriate context
- [NooBaa CLI](https://github.com/noobaa/noobaa-operator) installed

To install NooBaa CLI, follow this guideline: https://github.com/noobaa/noobaa.github.io/blob/master/noobaa-operator-cli.md

## Step 1: Deploy NooBaa to Kubernetes

```bash
# Create a dedicated namespace for NooBaa
kubectl create ns noobaa

# Set your kubectl context to the noobaa namespace
kubectl config set-context --current --namespace noobaa

# Install NooBaa with specific version
noobaa install \
    --operator-image=noobaa/noobaa-operator:5.18.3 \
    --noobaa-image=noobaa/noobaa-core:5.18.3
```

## Step 2: Verify Installation

```bash
# Check the status of NooBaa deployment
noobaa status
```
