import json

def lambda_handler(event, context):
    required_diagrams = [
        "C4-LEVEL1",
        "C4-LEVEL2",
        "C4-LEVEL3-A",
        "C4-LEVEL3-B"
    ]
    response = event.get("response", "")
    missing = [d for d in required_diagrams if d not in response]
    if not missing:
        return {
            "statusCode": 200,
            "response": response,
            "status": "COMPLETED"
        }
    instructions = (
        "The following C4 diagrams are missing: " + ", ".join(missing) + ". "
        "Please re-do your task and ensure the output includes these diagrams. "
        "Amend your response accordingly."
    )
    amended_request = f"You responded with: {response}\n\nThis is insufficient: {instructions}"
    return {
        "statusCode": 200,
        "request": amended_request,
        "status": "INSUFFICIENT"
    }
