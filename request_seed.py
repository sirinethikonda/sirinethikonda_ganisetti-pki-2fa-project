import requests

url = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

payload = {
    "student_id": "YOUR_ID",
    "github_repo_url": "https://github.com/sirinethikonda/sirinethikonda_ganisetti-pki-2fa-project",
    "public_key": """-----BEGIN PUBLIC KEY-----
YOUR PUBLIC KEY HERE
-----END PUBLIC KEY-----"""
}

response = requests.post(url, json=payload)

print(response.json())
