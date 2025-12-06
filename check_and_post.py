# check_and_post.py
import os, sys, requests
from cryptography.hazmat.primitives import serialization

PUB_FN = "student_public.pem"
URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
STUDENT_ID = "23a91a61f1"
REPO = "https://github.com/sirinethikonda/sirinethikonda_ganisetti-pki-2fa-project"

# 1) verify file exists
if not os.path.exists(PUB_FN):
    print("ERROR: public key file not found:", PUB_FN)
    sys.exit(1)

b = open(PUB_FN, "rb").read()
print("Loaded", PUB_FN, "size:", len(b))

# 2) try to load PEM locally (this confirms it's a valid PEM)
try:
    pub = serialization.load_pem_public_key(b)
    print("OK: student_public.pem loads locally as a PEM public key.")
except Exception as e:
    print("ERROR: student_public.pem failed to load locally. Exception:")
    print(e)
    print("\nIf this fails, regenerate the public key from your private key with the provided regen_pub.py script.")
    sys.exit(1)

# 3) Convert bytes -> decoded string using utf-8 (keeps real newline characters)
pub_text = b.decode("utf-8")

# 4) Build payload with raw multi-line PEM (requests will JSON-encode properly)
payload = {
    "student_id": STUDENT_ID,
    "github_repo_url": REPO,
    "public_key": pub_text
}

print("\nPosting payload to instructor API (public_key sent as multi-line PEM string)...")
try:
    r = requests.post(URL, json=payload, timeout=30)
except Exception as e:
    print("HTTP request failed:", e)
    sys.exit(1)

print("Status code:", r.status_code)
print("Response text:\n", r.text)

# 5) If we got encrypted_seed, save it
try:
    j = r.json()
    if "encrypted_seed" in j:
        open("encrypted_seed.txt", "w", encoding="ascii").write(j["encrypted_seed"])
        print("Saved encrypted_seed.txt")
except Exception:
    pass
