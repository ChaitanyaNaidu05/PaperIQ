import bcrypt


def generate_salt():
    return bcrypt.gensalt(rounds=12)


def hash_password(password, salt):
    return bcrypt.hashpw(password.encode(), salt)


def verify_password(stored_password, stored_salt, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password)
