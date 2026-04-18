import requests
import json

base_url = "http://localhost:11211/api/openai/v1"
model = "imagen-4.0-generate-001:latest"

print("--- Testing /images/generations ---")
try:
    resp = requests.post(f"{base_url}/images/generations", json={
        "model": model,
        "prompt": "A cute white cat",
        "n": 1,
        "size": "1024x1024"
    }, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Testing /chat/completions ---")
try:
    resp = requests.post(f"{base_url}/chat/completions", json={
        "model": model,
        "messages": [{"role": "user", "content": "Generate an image of a cute white cat"}]
    }, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
