#!/usr/bin/env bash
set -euo pipefail
PROJECT="${GOOGLE_CLOUD_PROJECT:-autobudget-470203}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
MODEL="${1:-gemini-2.5-pro}"
TOKEN="$(gcloud auth print-access-token)"
code="$(curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -X POST \
  "https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT}/locations/${REGION}/publishers/google/models/${MODEL}:generateContent" \
  -d '{"contents":[{"role":"user","parts":[{"text":"health check"}]}]}')"
echo "[health] HTTP: $code"
exit $([[ "$code" == "200" ]] && echo 0 || echo 1)
