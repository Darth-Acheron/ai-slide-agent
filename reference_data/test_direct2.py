import requests
import time

start = time.time()
print("Testing gemini-3.1-flash-image-preview:latest with b64_json...")
try:
    img_resp = requests.post("http://localhost:11211/api/openai/v1/images/generations", json={
        "model": "gemini-3.1-flash-image-preview:latest",
        "prompt": "A robot",
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json"
    }, timeout=200)
    print("Status:", img_resp.status_code)
    print("Time:", time.time() - start)
except Exception as e:
    print("Error:", e)
