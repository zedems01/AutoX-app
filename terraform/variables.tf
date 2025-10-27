variable "aws_region" {
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  type        = string
  default     = "autox"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets_cidr" {
  description = "The CIDR blocks for public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets_cidr" {
  description = "The CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "availability_zones" {
  description = "Availability zones for the subnets."
  type        = list(string)
  default     = ["eu-west-3a", "eu-west-3b"]
}

variable "ecr_repo_name" {
  description = "The name of the ECR repository for the backend."
  type        = string
  default     = "autox-backend"
}

variable "secrets" {
  description = "A map of secrets to store in AWS Secrets Manager."
  type        = map(string)
  sensitive   = true
}