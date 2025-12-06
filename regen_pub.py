# regen_pub.py
from cryptography.hazmat.primitives import serialization
with open("student_private.pem","rb") as f:
    priv = serialization.load_pem_private_key(f.read(), password=None)
pub = priv.public_key()
with open("student_public.pem","wb") as f:
    f.write(pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))
print("Regenerated student_public.pem from student_private.pem")
