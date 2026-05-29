import hmac
import hashlib
import os

def hash_string(input_string: str) -> str:
    """
    Hashes a string using HMAC-SHA256 and the HASH_SECRET from environment variables.
    """
    secret = os.getenv("HASH_SECRET", "default_secret_if_not_found")
    return hmac.new(
        secret.encode(),
        input_string.encode(),
        hashlib.sha256
    ).hexdigest()
