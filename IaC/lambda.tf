locals {
  agent_zips = fileset("${path.module}/../", "*_agent/*_agent.zip")
}

locals {
  agents = {
    for zip_path in local.agent_zips :
    regex("^([\\w-]+)_agent/([\\w-]+)_agent.zip$", zip_path)[1] => zip_path
    if length(regex("^([\\w-]+)_agent/([\\w-]+)_agent.zip$", zip_path)) > 0
  }
}

resource "aws_lambda_function" "agent" {
  for_each      = local.agents
  function_name =  "${each.key}_agent"
  handler       = "${each.key}_agent.lambda_handler"
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_exec.arn
  filename      = "${path.module}/../${each.value}"
  source_code_hash = filebase64sha256("${path.module}/../${each.value}")
  timeout       = 300
  environment {
    variables = {
      BEDROCK_ENDPOINT = var.endpoint_bedrock
      BEDROCK_REGION   = var.region
      BEDROCK_MODEL_ID = var.bedrock_model_id
    }
  }
}