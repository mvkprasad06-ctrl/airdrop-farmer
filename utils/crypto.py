"""AES-256 encryption for wallet storage."""
import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
ITERATIONS = 100_000

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode())

def encrypt_wallets(wallets: list[dict], password: str) -> bytes:
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    data = json.dumps(wallets, separators=(',', ':')).encode()
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return salt + nonce + ciphertext

def decrypt_wallets(encrypted: bytes, password: str) -> list[dict]:
    salt = encrypted[:SALT_SIZE]
    nonce = encrypted[SALT_SIZE:SALT_SIZE+NONCE_SIZE]
    ciphertext = encrypted[SALT_SIZE+NONCE_SIZE:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    data = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(data.decode())

def save_encrypted(wallets: list[dict], password: str, filepath: str):
    with open(filepath, 'wb') as f:
        f.write(encrypt_wallets(wallets, password))

def load_encrypted(password: str, filepath: str) -> list[dict]:
    with open(filepath, 'rb') as f:
        return decrypt_wallets(f.read(), password)