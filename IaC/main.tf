provider "aws" {
  region                      = var.region
  access_key                  = var.access_key
  secret_key                  = var.secret_key
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  endpoints {
    lambda    = var.endpoint_lambda
    iam       = var.endpoint_iam
    s3        = var.endpoint_s3
    bedrock   = var.endpoint_bedrock
    stepfunctions = var.endpoint_stepfunctions
  }
}

locals {
    name = var.project_name
}