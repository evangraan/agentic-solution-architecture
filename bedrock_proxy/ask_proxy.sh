curl -H "Content-Type: application/json" -X POST -d "{\"messages\":[{\"role\":\"user\",\"content\":[{\"text\":\"$1\"}]}]}" "http://localhost:9001/model/mistral/invoke"
