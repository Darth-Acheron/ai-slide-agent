import requests
print("Testing gemini-3.1-flash-image-preview:latest...")
try:
    img_resp = requests.post("http://localhost:11211/api/openai/v1/images/generations", json={
        "model": "gemini-3.1-flash-image-preview:latest",
        "prompt": "A robot",
        "n": 1,
        "size": "1024x1024"
    }, timeout=150)
    print("Status:", img_resp.status_code)
    print("Body:", img_resp.text[:200])
except Exception as e:
    print("Error:", e)
