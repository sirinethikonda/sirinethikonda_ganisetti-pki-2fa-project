# scripts/generated_commit_proof.py (Assumes keys are in the project root for local execution)
import base64
import sys
import os

# Adjust path to find app module for local execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.crypto_utils import (
    load_private_key,
    sign_message_p1,
    load_public_key,
    encrypt_with_public_key
)

# TODO: Replace this with your actual 40-character commit hash
# **CRITICAL: Get this from 'git log -1 --format=%H' AFTER your final commit**
commit_hash = "YOUR_40_CHAR_HASH" 

# NOTE: Key paths for LOCAL execution (adjust if keys are in a 'keys' subdir)
PRIV_KEY_PATH = "student_private.pem"
INST_PUB_KEY_PATH = "instructor_public.pem"

if not os.path.exists(PRIV_KEY_PATH) or not os.path.exists(INST_PUB_KEY_PATH):
    print("ERROR: Key files missing for local proof generation.")
    sys.exit(1)

# Load student private key
priv = load_private_key(PRIV_KEY_PATH)

# Sign commit hash using RSA-PSS
# CRITICAL: Message is the ASCII string of the hash
sig = sign_message_p1(commit_hash, priv)
print(f"1. Commit Hash: {commit_hash}")
print(f"2. Signature Size: {len(sig)} bytes")

# Load instructor public key
inst_pub = load_public_key(INST_PUB_KEY_PATH)

# Encrypt the signature with instructor public key
encrypted_sig = encrypt_with_public_key(sig, inst_pub)
print(f"3. Encrypted Signature Size: {len(encrypted_sig)} bytes")

# Output final Base64 encoded proof (single line)
base64_proof = base64.b64encode(encrypted_sig).decode('ascii')
print("\n4. Encrypted Commit Signature (BASE64, single line):")
print(base64_proof)