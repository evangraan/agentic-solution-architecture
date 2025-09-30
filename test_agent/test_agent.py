import boto3
import json
import os

def lambda_handler(event, context):
    endpoint_url = os.environ.get("BEDROCK_ENDPOINT")
    region_name = os.environ.get("BEDROCK_REGION")
    model_id = os.environ.get("BEDROCK_MODEL_ID")

    client = boto3.client("bedrock-runtime", endpoint_url=endpoint_url, region_name=region_name)
    response = client.invoke_model(
       modelId=model_id,
       contentType="application/json",
       accept="application/json",
       body=json.dumps({
           "input": "Say hello to Fatih"
       })
    )
    
    return {
        "statusCode": 200,
        "body": response["body"].read().decode()
    }