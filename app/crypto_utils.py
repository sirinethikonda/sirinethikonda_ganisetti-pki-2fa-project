# app/crypto_utils.py
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils, rsa
from cryptography.hazmat.backends import default_backend

def load_private_key(path: str):
    """Loads a private key from a PEM file."""
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

def load_public_key(path: str):
    """Loads a public key from a PEM file."""
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read(), backend=default_backend())

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypts a base64-encoded encrypted seed using RSA/OAEP with SHA-256.
    Returns: Decrypted hex seed (64-character string).
    """
    ciphertext = base64.b64decode(encrypted_seed_b64)
    
    # CRITICAL: Use correct parameters: OAEP, MGF1(SHA256), SHA256, label=None
    try:
        decrypted_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        # Catch decryption errors (e.g., wrong key, wrong parameters, malformed ciphertext)
        print(f"Decryption Error: {e}")
        raise ValueError("Decryption failed")
    
    # The decrypted seed is a 64-char hex string (32 bytes)
    hex_seed = decrypted_bytes.decode('utf-8')
    
    if len(hex_seed) != 64 or not all(c in '0123456789abcdef' for c in hex_seed.lower()):
        raise ValueError("Decrypted seed format invalid: not a 64-character hex string")
        
    return hex_seed

def sign_message_p1(commit_hash: str, private_key):
    """
    Signs a commit hash using RSA-PSS with SHA-256 and maximum salt length.
    CRITICAL: Signs the ASCII string, not binary hex.
    """
    message = commit_hash.encode("utf-8")
    
    # CRITICAL: Use correct parameters: PSS, MGF1(SHA256), SHA256, MAX_LENGTH
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypts data (signature) using RSA/OAEP with instructor's public key.
    """
    # CRITICAL: Use correct parameters: OAEP, MGF1(SHA256), SHA256, label=None
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext