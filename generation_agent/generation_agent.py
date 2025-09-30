import boto3
import json
import os

def lambda_handler(event, context):
    endpoint_url = os.environ.get("BEDROCK_ENDPOINT")
    region_name = os.environ.get("BEDROCK_REGION")
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    request_string = event.get("request", "default value")

    request_string += "\n\nOutput expected: you MUST produce a C4 level 1 diagram. Prefix it with C4-LEVEL1. You MUST produce a C4 level 2 diagram. Prefix it with C4-LEVEL2. You MUST produce two C4 level 3 diagrams, for the top two main technical design aspects. Prefix them with C4-LEVEL3-A and C4-LEVEL3-B"

    client = boto3.client("bedrock-runtime", endpoint_url=endpoint_url, region_name=region_name)
    response = client.invoke_model(
       modelId=model_id,
       contentType="application/json",
       accept="application/json",
       body=json.dumps({
           "input": request_string
       })
    )
    
    output = response["body"].read().decode()

    print(f"GENERATION_AGENT OUTPUT:{output}")

    return {
        "statusCode": 200,
        "response": output,  # chain for next agent in the step function orchestration
        "request": request_string
    }    
