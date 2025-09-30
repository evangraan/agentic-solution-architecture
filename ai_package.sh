rm -f ai_package.zip
zip ai_package.zip rag bedrock_proxy *.sh README.md *_agent IaC -x "rag/venv" -x "bedrock_proxy/venv" -x ".git" -x "bedrock_proxy/__pycache__" -x "rag/__pycache__"
