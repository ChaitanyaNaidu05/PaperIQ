import bcrypt
import logging

logger = logging.getLogger(__name__)


def generate_salt():
    return bcrypt.gensalt(rounds=12)


def hash_password(password, salt):
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode() if isinstance(hashed, bytes) else hashed


def verify_password(stored_password, stored_salt, provided_password):
    if isinstance(stored_password, str):
        stored_password = stored_password.encode()
    try:
        return bcrypt.checkpw(provided_password.encode(), stored_password)
    except (ValueError, TypeError) as e:
        logger.error(f"Password verification error: {e}")
        return False
