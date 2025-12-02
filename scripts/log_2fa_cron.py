#!/usr/bin/env python3
import os, base64, datetime
import pyotp

DATA = "/data/seed.txt"

def hex_to_base32(h):
    return base64.b32encode(bytes.fromhex(h)).decode()

try:
    if not os.path.exists(DATA):
        raise Exception("Seed missing")
    with open(DATA) as f:
        seed = f.read().strip()
    b32 = hex_to_base32(seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    code = totp.now()
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} - 2FA Code: {code}")
except Exception as e:
    import sys
    print(f"ERROR: {e}", file=sys.stderr)
