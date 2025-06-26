from hashlib import sha256


def hash_password(pssw: str) -> str:
    return sha256(pssw.encode()).hexdigest()
