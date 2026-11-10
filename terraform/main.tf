terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      lab = "terraform-vpc-clippy"
    }
  }
}

# Provided: the newest Ubuntu 24.04 image, read from the public AWS parameter store.
data "aws_ssm_parameter" "ubuntu" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

# TODO 1: a data source for the availability zones of the region (state = "available").

# TODO 2: the network
#   - aws_vpc (CIDR from var.vpc_cidr, DNS hostnames on)
#   - aws_internet_gateway
#   - TWO public subnets, in two DIFFERENT availability zones, without copying the block twice
#     (count or for_each). Give each a /24 carved out of the VPC range with cidrsubnet().
#   - one route table with 0.0.0.0/0 -> the internet gateway, associated with both subnets
#
# TODO 3: aws_security_group for the server
#   - HTTP (80) from anywhere
#   - SSH (22) from var.my_ip_cidr ONLY
#   - all outbound traffic
#   Use the separate aws_vpc_security_group_ingress_rule / egress_rule resources.
#
# TODO 4: aws_instance "clippy"
#   - t3.micro, the image above, in the FIRST public subnet, with a public IP
#   - IMDSv2 required (metadata_options)
#   - user_data = templatefile("${path.module}/userdata.sh.tftpl", { clippy_ref = "v0.2.0" })
#   - tag Name = "clippy-staging"
#   - make sure the internet gateway route exists before the server boots (depends_on)
#
# Tag everything: the provider default_tags above already put lab = "terraform-vpc-clippy" on it.
