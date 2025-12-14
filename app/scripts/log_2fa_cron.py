#!/usr/bin/env python3
# app/scripts/log_2fa_cron.py
import datetime
import os
import sys

# Ensure the app directory is in the path to import totp_utils
sys.path.append("/app") 
from app.totp_utils import generate_totp_code

# Paths are absolute inside the container
SEED_FILE = "/data/seed.txt"
# LOG_FILE = "/cron/last_code.txt" # We print to stdout, and cron redirects to this file

def now():
    """Get current UTC timestamp in required format."""
    # CRITICAL: Must use UTC
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    try:
        # 1. Read seed from persistent storage
        if not os.path.exists(SEED_FILE):
            print(f"{now()} - ERROR: Seed not found at {SEED_FILE}")
            sys.exit(1) # Exit with error code if seed is missing
        
        with open(SEED_FILE, "r") as f:
            seed = f.read().strip()
            
        # 2. Generate current TOTP code
        # generate_totp_code returns (code, remaining_seconds)
        code, _ = generate_totp_code(seed)
        
        # 3. Output formatted line
        print(f"{now()} - 2FA Code: {code}")
        
    except Exception as e:
        # Graceful error handling for the cron job
        print(f"{now()} - CRON JOB ERROR: {e}", file=sys.stderr)
        sys.exit(1)