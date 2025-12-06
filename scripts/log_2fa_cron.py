#!/usr/bin/env python3
import datetime, os
from app.totp_utils import generate_totp_code

SEED_FILE = "/data/seed.txt"
LOG_FILE = "/cron/last_code.txt"

def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

if not os.path.exists(SEED_FILE):
    print(f"{now()} - ERROR: Seed not found")
else:
    seed = open(SEED_FILE).read().strip()
    code = generate_totp_code(seed)
    print(f"{now()} - 2FA Code: {code}")
