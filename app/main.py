# app/main.py
import os
import json
import base64
from fastapi import FastAPI, APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from app.crypto_utils import load_private_key, decrypt_seed
from app.totp_utils import generate_totp_code, verify_totp_code

# Global FastAPI App
app = FastAPI(title="PKI-Based 2FA Microservice", version="1.0.0")
router = APIRouter()

# Constants
SEED_FILE_PATH = "/data/seed.txt"
PRIVATE_KEY_PATH = "/app/student_private.pem" # Path inside the container

# --- Pydantic Models for Request/Response Bodies ---

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str = Field(..., description="Base64-encoded RSA-OAEP encrypted seed.")

class DecryptSeedResponse(BaseModel):
    status: str = Field("ok", description="Status of the operation.")

class Verify2FARequest(BaseModel):
    code: str = Field(..., description="6-digit TOTP code.")

class Verify2FAResponse(BaseModel):
    valid: bool = Field(..., description="True if the code is valid, False otherwise.")

# --- Helper Functions ---

def read_seed_from_disk() -> str:
    """Reads the hex seed from persistent storage, raises HTTP 500 if missing."""
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(
            status_code=500,
            detail={"error": "Seed not decrypted yet."}
        )
    with open(SEED_FILE_PATH, "r") as f:
        hex_seed = f.read().strip()
    
    # Basic validation (64-char hex)
    if len(hex_seed) != 64 or not all(c in '0123456789abcdef' for c in hex_seed.lower()):
        # This should ideally not happen if decryption was correct, but good to check
        raise HTTPException(
            status_code=500,
            detail={"error": "Stored seed is corrupt."}
        )
        
    return hex_seed

# --- API Endpoints ---

@router.post("/decrypt-seed", response_model=DecryptSeedResponse)
async def decrypt_seed_endpoint(request: DecryptSeedRequest):
    """
    Accepts an encrypted seed, decrypts it using the student's private key,
    and stores the decrypted hex seed persistently.
    """
    # 1. Load Private Key
    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)
    except Exception as e:
        print(f"Error loading private key: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Server error: Could not load student private key."}
        )
        
    # 2. Decrypt Seed
    try:
        hex_seed = decrypt_seed(request.encrypted_seed, private_key)
    except (ValueError, Exception) as e:
        # Catches both crypto errors (ValueError) and general exceptions
        print(f"Decryption failed for encrypted seed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Decryption failed"}
        )
        
    # 3. Store persistently
    try:
        os.makedirs(os.path.dirname(SEED_FILE_PATH), exist_ok=True)
        with open(SEED_FILE_PATH, "w") as f:
            f.write(hex_seed)
    except Exception as e:
        print(f"File IO Error: Could not write seed to {SEED_FILE_PATH}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error: Could not store decrypted seed."}
        )
        
    return {"status": "ok"}

@router.get("/generate-2fa")
async def generate_2fa_code_endpoint():
    """
    Reads the stored seed, generates the current TOTP code, and calculates
    the remaining time in the current period.
    """
    hex_seed = read_seed_from_disk()
    
    try:
        code, remaining_seconds = generate_totp_code(hex_seed)
        
        return {
            "code": code,
            "valid_for": remaining_seconds
        }
    except Exception as e:
        print(f"TOTP generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "TOTP generation failed."}
        )

@router.post("/verify-2fa", response_model=Verify2FAResponse)
async def verify_2fa_endpoint(request: Verify2FARequest):
    """
    Verifies a 6-digit TOTP code against the stored seed with ±1 period tolerance.
    """
    # 1. Validate input
    if not request.code or len(request.code) != 6 or not request.code.isdigit():
        raise HTTPException(
            status_code=400,
            detail={"error": "Missing or invalid code format."}
        )

    # 2. Read seed
    hex_seed = read_seed_from_disk()
    
    # 3. Verify code
    try:
        # valid_window=1 means ±1 period (±30 seconds) tolerance
        is_valid = verify_totp_code(hex_seed, request.code, valid_window=1)
        
        return {"valid": is_valid}
    except Exception as e:
        print(f"TOTP verification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "TOTP verification failed."}
        )

# Register the router to the main app
app.include_router(router)