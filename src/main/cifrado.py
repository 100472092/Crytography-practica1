import os
import base64

import cryptography.exceptions
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def hash_password(user_pw: str):
    salt = os.urandom(16)

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**15,
        r=8,
        p=1)

    password_token = kdf.derive(bytes(user_pw, "ascii"))
    password_token = base64.b64encode(password_token).decode('ascii')

    salt = base64.b64encode(salt).decode('ascii')
    return password_token, salt


def verify_pw(in_pw: str, password_token: str, salt:str):
    salt = bytes(salt, 'ascii')
    password_token = bytes(password_token, 'ascii')

    salt = base64.b64decode(salt)
    password_token = base64.b64decode(password_token)

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**15,
        r=8,
        p=1)

    try:
        kdf.verify(bytes(in_pw, "ascii"), password_token)
        return True
    except cryptography.exceptions.InvalidKey:
        return False
