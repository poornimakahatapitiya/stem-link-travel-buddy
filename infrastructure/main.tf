# Main Terraform configuration for Travel Buddy Application
data "aws_region" "current" {}
# Data source for current region

data "aws_caller_identity" "current" {}
# Data source for current AWS account

}
  state = "available"
data "aws_availability_zones" "available" {
# Data source for availability zones

}
  }
    }
      Application = "TravelBuddy"
      ManagedBy   = "Terraform"
      Environment = var.environment
      Project     = var.project_name
    tags = {
  default_tags {

  region = var.aws_region
provider "aws" {

}
  # }
  #   dynamodb_table = "terraform-state-lock"
  #   encrypt        = true
  #   region         = "us-east-1"
  #   key            = "travel-buddy/terraform.tfstate"
  #   bucket         = "your-terraform-state-bucket"
  # backend "s3" {
  # Uncomment and configure for remote state management

  }
    }
      version = "~> 5.0"
      source  = "hashicorp/aws"
    aws = {
  required_providers {

  required_version = ">= 1.0"
terraform {

# This file orchestrates all the infrastructure resources

