pip install -r requirements.txt
#REQUESTS_CA_BUNDLE="/path/to/additional-ca.pem" uvicorn bedrock_api_proxy:app --host 0.0.0.0 --port 9001
uvicorn bedrock_api_proxy:app --host 0.0.0.0 --port 9001
