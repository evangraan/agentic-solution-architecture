variable "region" {
    description = "AWS region that supports bedrock"
    type = string
    default = "us-east-1"
}

variable "foundation_model" {
    description = "bedrock foundation model of choice"
    type = string
    default = "mistral"
}

variable "project_name" {
    type = string
    default = "Agentic bedrock agent workflow solution"
}

variable "access_key" {
    type = string
    default = "test"
}

variable "secret_key" {
    type = string
    default = "test"
}

variable "endpoint_iam" {
    type = string
    default = "http://localhost:4566"
}

variable "endpoint_lambda" {
    type = string
    default = "http://localhost:4566"
}

variable "endpoint_s3" {
    type = string
    default = "http://localhost:4566"
}

variable "endpoint_bedrock" {
    type = string
    default = "http://host.lima.internal:11435"
}

variable "endpoint_stepfunctions" {
    type = string
    default = "http://localhost:4566"
}

variable "bedrock_model_id" {
    type = string
    default = "mistral"
}
