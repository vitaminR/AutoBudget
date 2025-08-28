# Vertex + gcloud Troubleshooting Toolkit

Use this toolkit to quickly setup & verify Vertex AI connectivity.

## Structure
- setup/   — first-run project/account/API enable
- env/     — set env vars for this shell (WSL or PowerShell)
- checks/  — health, list publisher models, token check
- calls/   — minimal generateContent example
- utils/   — probe models, cleanup env

Default: project=autobudget-470203, region=us-central1, model=gemini-2.5-pro

## Quickstart
source env/01_env_wsl.sh
setup/00_setup_project.sh
checks/10_health.sh
calls/20_generate_text.sh "Say hello in one sentence"
