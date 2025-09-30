from urllib import response
import boto3
import json
import os

def lambda_handler(event, context):
    endpoint_url = os.environ.get("BEDROCK_ENDPOINT")
    region_name = os.environ.get("BEDROCK_REGION")
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    request_string = event.get("request", "default value")

    client = boto3.client("bedrock-runtime", endpoint_url=endpoint_url, region_name=region_name)
    response = client.invoke_model(
       modelId=model_id,
       contentType="application/json",
       accept="application/json",
       body=json.dumps({
           "input": f"Analyse this input requirement and turn it into a prompt for the bedrock foundational model. The prompt MUST start with PROMPT and include only the prompt you generated, no wrapping text of any kind. The only output present must be the prompt you generated, followed by a single search term you would use to ask the wikipedia API for enrichment for the prompt. Output the search term (MUST be 10 characers or less no spaces and MUST be preceded by SEARCH) only after the prompt and no other text.: {request_string}"
       })
    )
    
    output = response["body"].read().decode()
    return {
        "statusCode": 200,
        "request": output # chain for next agent in the step function orchestration
    }