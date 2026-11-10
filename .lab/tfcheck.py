#!/usr/bin/env python3
import json, os, re, subprocess, sys, time, urllib.request, urllib.error
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
passed = failed = 0


def check(desc, ok, hint=""):
    global passed, failed
    if ok:
        passed += 1; print("PASS  " + desc)
    else:
        failed += 1; print("FAIL  " + desc + (("   -> " + hint) if hint else ""))


def aws(*a):
    try:
        return json.loads(subprocess.check_output(("aws",) + a + ("--output", "json"), stderr=subprocess.DEVNULL, timeout=60) or "null")
    except Exception:
        return None


def sh(c, env=None):
    r = subprocess.run(c, shell=True, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


F = "Name=tag:lab,Values=terraform-vpc-clippy"
print("== Your code ==")
tf = sh("cat terraform/*.tf")[1]
check("terraform fmt -check is clean", sh("terraform -chdir=terraform fmt -check")[0] == 0, "terraform -chdir=terraform fmt")
vars_ = sh("cat terraform/variables.tf")[1]
m = re.search(r'variable\s+"my_ip_cidr"\s*\{(.*?)\n\}', vars_, re.S)
check("variable my_ip_cidr exists, has NO default and has a validation block", bool(m) and "default" not in m.group(1) and "validation" in m.group(1))
check("the subnets use count or for_each (not copy-pasted blocks)", len(re.findall(r'resource\s+"aws_subnet"', tf)) == 1 and ("count" in tf or "for_each" in tf))
check("cidrsubnet() is used to carve the subnets out of the VPC range", "cidrsubnet" in tf)
check("user data comes from templatefile()", "templatefile" in tf)
tracked = sh("git ls-files")[1].split("\n")
check("no state file, .terraform/ or tfvars committed", not [f for f in tracked if re.search(r"\.tfstate|(^|/)\.terraform/|\.tfvars$", f)])
check("no AWS keys in the repository", sh("git grep -lE 'AKIA[0-9A-Z]{16}' -- . ':!.lab' ':!verify.sh'")[1].strip() == "")

print("== The infrastructure in AWS ==")
vpcs = (aws("ec2", "describe-vpcs", "--filters", F) or {}).get("Vpcs", [])
check("a VPC tagged lab=terraform-vpc-clippy exists", len(vpcs) == 1)
if not vpcs:
    print("\nNothing else can be checked without the VPC.\n%d check(s) failed, %d passed" % (failed, passed)); sys.exit(1)
vid = vpcs[0]["VpcId"]
VF = "Name=vpc-id,Values=" + vid
subs = (aws("ec2", "describe-subnets", "--filters", VF) or {}).get("Subnets", [])
check("two subnets in two different availability zones", len(subs) == 2 and len({s["AvailabilityZone"] for s in subs}) == 2)
import ipaddress
vnet = ipaddress.ip_network(vpcs[0]["CidrBlock"])
check("every subnet lies inside the VPC range and is a /24", all(ipaddress.ip_network(s["CidrBlock"]).subnet_of(vnet) and s["CidrBlock"].endswith("/24") for s in subs) and bool(subs))
igws = (aws("ec2", "describe-internet-gateways", "--filters", "Name=attachment.vpc-id,Values=" + vid) or {}).get("InternetGateways", [])
check("an internet gateway is attached", len(igws) == 1)
rts = (aws("ec2", "describe-route-tables", "--filters", VF) or {}).get("RouteTables", [])
def to_igw(sid):
    rt = next((r for r in rts if any(a.get("SubnetId") == sid for a in r["Associations"])), None)
    return bool(rt) and any(x.get("DestinationCidrBlock") == "0.0.0.0/0" and x.get("GatewayId", "").startswith("igw-") for x in rt["Routes"])
check("both subnets route 0.0.0.0/0 to the internet gateway", len(subs) == 2 and all(to_igw(s["SubnetId"]) for s in subs))
check("no NAT Gateway (it would cost money and this lab does not need one)", not (aws("ec2", "describe-nat-gateways", "--filter", VF, "Name=state,Values=available,pending") or {}).get("NatGateways"))
insts = []
for r in (aws("ec2", "describe-instances", "--filters", F, "Name=instance-state-name,Values=running,pending") or {}).get("Reservations", []):
    insts += r["Instances"]
check("exactly one running server named clippy-staging, type t3.micro",
      len(insts) == 1 and insts[0]["InstanceType"] == "t3.micro" and any(t["Key"] == "Name" and t["Value"] == "clippy-staging" for t in insts[0].get("Tags", [])))
inst = insts[0] if insts else {}
check("IMDSv2 is required", inst.get("MetadataOptions", {}).get("HttpTokens") == "required")
check("the server is in the first subnet and has a public IP", bool(inst.get("PublicIpAddress")) and inst.get("SubnetId") in [s["SubnetId"] for s in subs])
sgs = [g["GroupId"] for g in inst.get("SecurityGroups", [])]
rules = (aws("ec2", "describe-security-group-rules", "--filters", "Name=group-id,Values=" + ",".join(sgs)) or {}).get("SecurityGroupRules", []) if sgs else []
ing = [r for r in rules if not r["IsEgress"]]
check("security group: port 80 from anywhere, port 22 from ONE /32 address, nothing else",
      sorted((r["FromPort"], r.get("CidrIpv4")) for r in ing if r["FromPort"] == 80) == [(80, "0.0.0.0/0")]
      and len([r for r in ing if r["FromPort"] == 22]) == 1
      and all(r.get("CidrIpv4", "").endswith("/32") for r in ing if r["FromPort"] == 22)
      and all(r["FromPort"] in (22, 80) for r in ing))

print("== The live app ==")
ip = inst.get("PublicIpAddress")
def http(url, data=None, t=10):
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=t) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""
if ip:
    st = 0
    for _ in range(40):
        st, _ = http("http://%s/healthz" % ip)
        if st == 200:
            break
        time.sleep(5)
    check("GET http://<public ip>/healthz answers 200 (the user data finished; this takes 1-2 minutes after apply)", st == 200)
    st, body = http("http://%s/shorten" % ip, b'{"url":"https://ironhack.com"}')
    check("POST /shorten returns a short link", st in (200, 201) and "short_url" in body)
else:
    check("the server has a public IP to test", False)

print("== Terraform state ==")
rc, out = sh("terraform -chdir=terraform state list")
check("the state tracks the VPC, the subnets and the server", rc == 0 and "aws_instance." in out and "aws_vpc." in out and out.count("aws_subnet.") >= 2)
cidr = next((r["CidrIpv4"] for r in ing if r["FromPort"] == 22), "203.0.113.1/32")
env = dict(os.environ, TF_VAR_my_ip_cidr=cidr)
rc, out = sh("terraform -chdir=terraform plan -detailed-exitcode -input=false -no-color", env=env)
check("terraform plan finds nothing to change", rc == 0, "plan exit code %d" % rc)
check("terraform output url prints the address", sh("terraform -chdir=terraform output -raw url")[1].strip() == "http://%s/" % ip)

print()
print(("ALL CHECKS PASSED (%d/%d)" % (passed, passed)) if failed == 0 else ("%d check(s) failed, %d passed" % (failed, passed)))
sys.exit(1 if failed else 0)
