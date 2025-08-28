#!/usr/bin/env bash
set -euo pipefail
PROJECT="${GOOGLE_CLOUD_PROJECT:-autobudget-470203}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
TOKEN="$(gcloud auth print-access-token)"
MODELS=("gemini-2.5-pro" "gemini-2.5-pro-001" "gemini-2.0-pro" "gemini-1.5-pro" "text-embedding-005")
for MODEL in "${MODELS[@]}"; do
  code="$(curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -X POST \
    "https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT}/locations/${REGION}/publishers/google/models/${MODEL}:generateContent" \
    -d '{"contents":[{"role":"user","parts":[{"text":"health check"}]}]}')"
  echo "$(printf '%-20s %s\n' "$MODEL" "$code")"
done
