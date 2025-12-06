# main.py (FastAPI Example)

from fastapi import APIRouter, HTTPException

router = APIRouter()

# CRITICAL: The path must be an exact match: /generate-2fa
@router.get("/generate-2fa")
async def generate_2fa_code_endpoint():
    # 1. Read seed from /data/seed.txt
    try:
        with open("/data/seed.txt", "r") as f:
            hex_seed = f.read().strip()
    except FileNotFoundError:
        # 500 Internal Server Error if the seed is missing
        raise HTTPException(
            status_code=500, 
            detail={"error": "Seed not decrypted yet."}
        )

    # ... Your TOTP generation logic here ...
    
    # Return 200 OK response
    return {"code": "123456", "valid_for": 15}

# If you use a router, ensure it's included in the main app without a base path 
# prefix that would change the URL.