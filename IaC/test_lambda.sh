aws lambda invoke --function-name test_agent --payload '{}' --endpoint-url http://localhost:4566 --profile localstack output.json
cat output.json
