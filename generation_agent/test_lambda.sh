aws lambda invoke --function-name generation_agent --cli-binary-format raw-in-base64-out --payload "{\"request\": \"$1\"}" --endpoint-url http://localhost:4566 --profile localstack output.json
cat output.json
