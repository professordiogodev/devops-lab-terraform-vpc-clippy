#!/usr/bin/env bash
# Destroys everything this lab created. Run with: ./teardown.sh
set -u
cd "$(dirname "$0")/terraform" 2>/dev/null || { echo "No terraform/ directory." >&2; exit 1; }
aws sts get-caller-identity >/dev/null 2>&1 || { echo "No working AWS credentials." >&2; exit 1; }
# destroy does not care about the value of the variable, it only needs one
terraform destroy -auto-approve -input=false -var "my_ip_cidr=203.0.113.1/32"
echo "Now run ./verify-teardown.sh"
