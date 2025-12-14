# app/totp_utils.py (Final Corrected Version - Bypass Constant)
import pyotp
import base64
import time

# TOTP Configuration
PERIOD = 30
DIGITS = 6
# REMOVED: ALGORITHM = ... (relying on pyotp's SHA1 default)

def hex_to_base32(hex_seed: str) -> str:
    # ... (same as before) ...
    try:
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8').rstrip('=')
        return base32_seed
    except Exception as e:
        print(f"Hex to Base32 conversion failed: {e}")
        raise ValueError("Invalid hex seed format for Base32 conversion")

def get_totp_object(base32_seed: str):
    """Returns a configured pyotp.TOTP object."""
    return pyotp.TOTP(
        base32_seed,
        digits=DIGITS,
        interval=PERIOD
        # CRITICAL: Removed digest=ALGORITHM
    )

def generate_totp_code(hex_seed: str) -> str:
    # ... (same as before) ...
    base32_seed = hex_to_base32(hex_seed)
    totp = get_totp_object(base32_seed)
    
    code = totp.now()
    remaining_seconds = PERIOD - int(time.time() % PERIOD)
    
    return code, remaining_seconds

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    # ... (same as before) ...
    base32_seed = hex_to_base32(hex_seed)
    totp = get_totp_object(base32_seed)
    
    return totp.verify(code, valid_window=valid_window)