# app/main.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import base64, os, time, re
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp
import base64 as b64

app = FastAPI()

SEED_PATH = "/data/seed.txt"
PRIVATE_KEY_PATH = "student_private.pem"

hex_re = re.compile(r'^[0-9a-f]{64}$')

class DecryptSeedReq(BaseModel):
    encrypted_seed: str

class VerifyReq(BaseModel):
    code: str

def load_private_key():
    if not os.path.exists(PRIVATE_KEY_PATH):
        raise FileNotFoundError("Private key not found")
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def decrypt_seed_b64(encrypted_b64: str) -> str:
    try:
        ct = base64.b64decode(encrypted_b64)
    except Exception:
        raise ValueError("Invalid base64")
    priv = load_private_key()
    try:
        pt = priv.decrypt(
            ct,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                         algorithm=hashes.SHA256(),
                         label=None)
        )
    except Exception as e:
        raise ValueError("Decryption failed: " + str(e))
    s = pt.decode("utf-8").strip()
    if not hex_re.match(s):
        raise ValueError("Decrypted seed is not 64-char hex")
    return s

def hex_to_base32(hex_seed: str) -> str:
    b = bytes.fromhex(hex_seed)
    return b64.b32encode(b).decode('utf-8')

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/decrypt-seed")
def decrypt_seed(req: DecryptSeedReq):
    try:
        hex_seed = decrypt_seed_b64(req.encrypted_seed)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    os.makedirs(os.path.dirname(SEED_PATH), exist_ok=True)
    with open(SEED_PATH, "w") as f:
        f.write(hex_seed)
    return {"status": "ok"}

@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    hex_seed = open(SEED_PATH).read().strip()
    if not hex_re.match(hex_seed):
        raise HTTPException(status_code=500, detail="Invalid seed format")
    base32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32, digits=6, interval=30)
    code = totp.now()
    remaining = 30 - int(time.time() % 30)
    return {"code": code, "valid_for": remaining}

@app.post("/verify-2fa")
def verify_2fa(req: VerifyReq):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    hex_seed = open(SEED_PATH).read().strip()
    base32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32, digits=6, interval=30)
    valid = totp.verify(req.code, valid_window=1)
    return {"valid": bool(valid)}
