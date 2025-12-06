import json, requests

with open("payload.json","r",encoding="ascii") as f:
    payload = json.load(f)

url = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
resp = requests.post(url, json=payload, timeout=15)
print(resp.status_code)
print(resp.text)
