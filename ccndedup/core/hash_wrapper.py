from cryptography.hazmat.primitives import hashes
from spooky import hash128

def fash_hash(s: bytes):
    return hash128(s)

def slow_hash(s: bytes):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(s)
    return digest.finalize()
