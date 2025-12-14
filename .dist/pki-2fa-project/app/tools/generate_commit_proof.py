import base64
from app.crypto_utils import (
    load_private_key,
    sign_message_p1,
    load_public_key,
    encrypt_with_public_key
)

# TODO: Replace this with your actual 40-character commit hash
commit_hash = "YOUR_40_CHAR_HASH"

# Load student private key
priv = load_private_key("student_private.pem")

# Sign commit hash using RSA-PSS
sig = sign_message_p1(commit_hash, priv)

# Load instructor public key
inst_pub = load_public_key("instructor_public.pem")

# Encrypt the signature with instructor public key
encrypted_sig = encrypt_with_public_key(sig, inst_pub)

# Output final Base64 encoded proof
print(base64.b64encode(encrypted_sig).decode())
