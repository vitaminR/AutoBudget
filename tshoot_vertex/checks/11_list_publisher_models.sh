#!/usr/bin/env bash
set -euo pipefail
PROJECT="${GOOGLE_CLOUD_PROJECT:-autobudget-470203}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
TOKEN="$(gcloud auth print-access-token)"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT}/locations/${REGION}/publishers/google/models" \
  | python3 - <<'PY'
import sys, json
data=json.load(sys.stdin)
for m in data.get("models", [])[:20]:
    print(f"{m.get('displayName','?'):25} {m.get('name','?')} v:{m.get('versionId','?')}")
PY
