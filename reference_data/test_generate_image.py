import requests

try:
    resp = requests.post("http://localhost:8080/api/generate_image", json={"prompt": "A robot"}, timeout=10)
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)
except Exception as e:
    print("ERROR:", e)
