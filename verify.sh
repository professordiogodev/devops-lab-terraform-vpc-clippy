#!/usr/bin/env bash
# Checks your Terraform and the real infrastructure. Run with: ./verify.sh
cd "$(dirname "$0")" || exit 1
command -v terraform >/dev/null || { echo "Terraform is not installed." >&2; exit 1; }
aws sts get-caller-identity >/dev/null 2>&1 || { echo "No working AWS credentials." >&2; exit 1; }
exec python3 .lab/tfcheck.py
