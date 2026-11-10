variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

# TODO 5: variable "my_ip_cidr": your public IP as a /32 (curl -s https://checkip.amazonaws.com).
#         It must have NO default value. Add a validation block that rejects anything that is not a valid CIDR.
