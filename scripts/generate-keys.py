# scripts/generate_keys.py
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path

p = Path(__file__).resolve().parents[1]  # project root
keys = p / "keys"
keys.mkdir(exist_ok=True)

private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
priv_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

pub_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# write files
(keys / "student_private.pem").write_bytes(priv_pem)
(keys / "student_public.pem").write_bytes(pub_pem)

print("Generated keys:")
print(" -", (keys / "student_private.pem").resolve())
print(" -", (keys / "student_public.pem").resolve())
