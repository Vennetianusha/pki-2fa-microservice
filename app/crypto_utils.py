from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64

def load_private_key(path='student_private.pem'):
    with open(path,'rb') as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key(path):
    with open(path,'rb') as f:
        return serialization.load_pem_public_key(f.read())

def rsa_oaep_decrypt_b64(encrypted_b64: str, private_key):
    ct = base64.b64decode(encrypted_b64)
    pt = private_key.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return pt.decode('utf-8')

def sign_commit_hash_ascii(commit_hash: str, private_key):
    sig = private_key.sign(
        commit_hash.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return sig

def encrypt_with_public_key(data: bytes, public_key):
    ct = public_key.encrypt(
       data,
       padding.OAEP(
           mgf=padding.MGF1(algorithm=hashes.SHA256()),
           algorithm=hashes.SHA256(),
           label=None
       )
    )
    return ct
