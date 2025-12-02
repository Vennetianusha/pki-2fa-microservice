from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, time, base64
import pyotp
from crypto_utils import load_private_key, rsa_oaep_decrypt_b64

app = FastAPI()

DATA_PATH = "/data/seed.txt"
PRIVATE_KEY_PATH = "student_private.pem"

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

def read_seed():
    if not os.path.exists(DATA_PATH):
        return None
    with open(DATA_PATH, "r") as f:
        return f.read().strip()

def hex_to_base32(hex_seed):
    raw = bytes.fromhex(hex_seed)
    return base64.b32encode(raw).decode()

@app.post("/decrypt-seed")
def decrypt_seed(data: DecryptRequest):
    try:
        priv = load_private_key(PRIVATE_KEY_PATH)
        seed = rsa_oaep_decrypt_b64(data.encrypted_seed, priv)

        if len(seed) != 64 or any(c not in '0123456789abcdef' for c in seed):
            raise Exception("Invalid seed format")

        os.makedirs("/data", exist_ok=True)
        with open(DATA_PATH, "w") as f:
            f.write(seed)

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error":"Decryption failed","msg":str(e)})

@app.get("/generate-2fa")
def generate_2fa():
    seed = read_seed()
    if not seed:
        raise HTTPException(status_code=500, detail={"error":"Seed not found"})
    b32 = hex_to_base32(seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    code = totp.now()
    valid_for = 30 - (int(time.time()) % 30)
    return {"code": code, "valid_for": valid_for}

@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail={"error":"Missing code"})
    seed = read_seed()
    if not seed:
        raise HTTPException(status_code=500, detail={"error":"Seed not found"})
    b32 = hex_to_base32(seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    valid = totp.verify(req.code, valid_window=1)
    return {"valid": bool(valid)}
