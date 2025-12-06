from cryptography.hazmat.primitives import serialization

p = "student_public.pem"
with open(p, "rb") as f:
    data = f.read()
try:
    serialization.load_pem_public_key(data)
    print("OK: public key loads as PEM SubjectPublicKeyInfo")
except Exception as e:
    print("ERROR:", e)
