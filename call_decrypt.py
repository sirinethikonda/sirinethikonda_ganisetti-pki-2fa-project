# call_decrypt.py
import json, requests, sys, os
fn = "encrypted_seed.txt"
if not os.path.exists(fn):
    print("ERROR: encrypted_seed.txt missing"); sys.exit(1)
enc = open(fn,"r",encoding="ascii").read().strip()
payload = {"encrypted_seed": enc}
try:
    r = requests.post("http://127.0.0.1:8080/decrypt-seed", json=payload, timeout=10)
    print("Status:", r.status_code)
    print("Body:", r.text)
except Exception as e:
    print("REQUEST ERROR:", e)
