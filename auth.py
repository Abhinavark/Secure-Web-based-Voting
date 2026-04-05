import bcrypt

def hash_password(plain_text_password: str) -> bytes:
    """Hashes a password with a securely generated salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed

def verify_voter(plain_text_password: str, hashed_password: bytes) -> bool:
    """Verifies the voter's identity credentials."""
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)

# TODO: Add logic to generate a one-time cryptographic token once verified,
# and mark the voter's ID as "has_voted" in the database.
