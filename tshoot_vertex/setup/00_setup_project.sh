#!/usr/bin/env bash
set -euo pipefail
PROJECT="${GOOGLE_CLOUD_PROJECT:-autobudget-470203}"
ACCOUNT="${1:-gemini-cli-user-v2@autobudget-470203.iam.gserviceaccount.com}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"

echo "[setup] project: $PROJECT | region: $REGION | account: $ACCOUNT"
gcloud config set account "$ACCOUNT"
gcloud config set project "$PROJECT"
gcloud services enable aiplatform.googleapis.com
gcloud components install beta -q || true
echo "[setup] done."
