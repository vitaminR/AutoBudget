#!/usr/bin/env bash
set -euo pipefail
PROJECT="${GOOGLE_CLOUD_PROJECT:-autobudget-470203}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
MODEL="${MODEL:-gemini-2.5-pro}"
PROMPT="${1:-Say hello in one short sentence}"
TOKEN="$(gcloud auth print-access-token)"
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -X POST \
  "https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT}/locations/${REGION}/publishers/google/models/${MODEL}:generateContent" \
  -d "{\"contents\":[{\"role\":\"user\",\"parts\":[{\"text\":\"${PROMPT}\"}]}]}" \
  | python3 -m json.tool | head -n 40
