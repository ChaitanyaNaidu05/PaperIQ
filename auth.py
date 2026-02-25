import bcrypt


def generate_salt():
    return bcrypt.gensalt(rounds=12)


def hash_password(password, salt):
    hashed = bcrypt.hashpw(password.encode(), salt)
    # Return as string for database storage
    return hashed.decode() if isinstance(hashed, bytes) else hashed


def verify_password(stored_password, stored_salt, provided_password):
    # Convert stored_password to bytes if it's a string
    # bcrypt hashes include the salt, so we don't need stored_salt separately
    if isinstance(stored_password, str):
        stored_password = stored_password.encode()
    try:
        return bcrypt.checkpw(provided_password.encode(), stored_password)
    except (ValueError, TypeError) as e:
        logger = __import__('logging').getLogger(__name__)
        logger.error(f"Password verification error: {e}")
        return False
