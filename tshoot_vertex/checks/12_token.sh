#!/usr/bin/env bash
gcloud auth print-access-token | head -c 20; echo " ... token OK"
