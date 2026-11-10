#!/usr/bin/env bash
rc=0
ls terraform/*.tf >/dev/null 2>&1 && echo "- ✅ terraform/ has .tf files" || { echo "- ❌ terraform/ has no .tf files"; rc=1; }
grep -q 'aws_instance' terraform/main.tf && grep -q 'aws_vpc' terraform/main.tf && echo "- ✅ the network and the server are in the code" || { echo "- ❌ aws_vpc / aws_instance missing from main.tf"; rc=1; }
if git ls-files | grep -qE '\.tfstate|\.terraform/|\.tfvars$'; then echo "- ❌ state, .terraform/ or tfvars is committed"; rc=1; else echo "- ✅ no state or .terraform/ committed"; fi
grep -rEq 'AKIA[0-9A-Z]{16}' . --exclude-dir=.git --exclude=tfcheck.py && { echo "- ❌ an AWS access key is committed"; rc=1; } || echo "- ✅ no AWS access key committed"
grep -qE '^ALL CHECKS PASSED \(' SUBMISSION.md && echo "- ✅ SUBMISSION.md shows ALL CHECKS PASSED" || { echo "- ❌ paste the verify.sh output ('ALL CHECKS PASSED') into SUBMISSION.md"; rc=1; }
exit $rc
