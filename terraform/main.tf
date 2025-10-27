terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # S3 backend + DynamoDB for remote state storage
  backend "s3" {
    bucket         = "autox-terraform-state"
    key            = "autox.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "autox-terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}