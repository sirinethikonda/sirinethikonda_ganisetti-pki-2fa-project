import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key(path="/app/student_private.pem"):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def decrypt_seed(encrypted_seed_b64, private_key):
    ciphertext = base64.b64decode(encrypted_seed_b64)
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    seed = plaintext.decode().strip()

    # Validate 64-character hex
    if len(seed) != 64:
        raise ValueError("Invalid seed format")
    return seed
