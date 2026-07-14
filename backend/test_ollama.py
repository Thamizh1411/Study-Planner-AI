import httpx

response = httpx.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3.2:latest",
        "messages": [
            {
                "role": "user",
                "content": "What is an operating system?"
            }
        ],
        "stream": False
    },
    timeout=60
)

print("Status Code:", response.status_code)
print("Response:")
print(response.text)