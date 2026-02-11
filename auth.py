import hashlib
import os

def generate_salt():
    return os.urandom(32).hex()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(stored_password, stored_salt, provided_password):
    return stored_password == hashlib.sha256((provided_password + stored_salt).encode()).hexdigest()
