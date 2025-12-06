import pyotp, base64, time

def hex_to_base32(hex_seed):
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode()

def generate_totp_code(hex_seed):
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.now()

def verify_totp(hex_seed, code):
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.verify(code, valid_window=1)

def seconds_remaining():
    return 30 - (int(time.time()) % 30)
