"""
auth.py
-------
Minimal username/password auth helpers (salted SHA-256) for a student /
portfolio project. Good enough to give every user their own account and
their own data - not intended as bank-grade security.
"""

import hashlib
import os


def hash_password(password: str, salt: str = None) -> str:
    """Return 'salt$hash' so the salt travels with the stored hash."""
    salt = salt or os.urandom(16).hex()
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return hash_password(password, salt) == stored
