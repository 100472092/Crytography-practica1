import os
import base64

import cryptography.exceptions
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Genera un salt y lo usa para derivar la contraseña del usuario.
def hash_password(user_pw: str):
    salt = os.urandom(16)

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2 ** 15,
        r=8,
        p=1)

    password_token = kdf.derive(bytes(user_pw, "ascii"))
    password_token = base64.b64encode(password_token).decode('ascii')

    salt = base64.b64encode(salt).decode('ascii')
    return password_token, salt


# Función que verifica que la contraseña introducida por el usuario y la almacenada en el sistema es la misma.
def verify_pw(in_pw: str, password_token: str, salt: str):
    salt = bytes(salt, 'ascii')
    password_token = bytes(password_token, 'ascii')

    salt = base64.b64decode(salt)
    password_token = base64.b64decode(password_token)

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2 ** 15,
        r=8,
        p=1)

    try:
        kdf.verify(bytes(in_pw, "ascii"), password_token)
        return True
    except cryptography.exceptions.InvalidKey:
        return False


# Realiza el cifrado autenticado de datos usando una clave proporcionada más un nonce que se genera. Utiliza
# ChaCha20Poly1305
def cifrado_autenticado(new_data, derived_key):
    derived_key = base64.b64decode(bytes(derived_key, 'ascii'))
    chacha = ChaCha20Poly1305(derived_key)
    nonce = os.urandom(12)
    encrypted_data = chacha.encrypt(nonce, bytes(new_data, 'ascii'), None)
    encrypted_data = base64.b64encode(encrypted_data).decode('ascii')
    nonce = base64.b64encode(nonce).decode('ascii')
    return encrypted_data, nonce


# Descifra los datos con una contraseña proporcionada y el nonce relacionado con estos datos.
def descifrado_autenticado(derived_key, nonce, encrypted_data):
    derived_key = base64.b64decode(bytes(derived_key, 'ascii'))
    encrypted_data = base64.b64decode(bytes(encrypted_data, 'ascii'))
    nonce = base64.b64decode(bytes(nonce, 'ascii'))
    chacha = ChaCha20Poly1305(derived_key)
    clear_data = chacha.decrypt(nonce, encrypted_data, None)
    clear_data = clear_data.decode('ascii')
    return clear_data


# Genera un salt que utiliza para derivar una clave utilizando PBKDF2HMAC.
def derivar_key(pw, salt_key):
    salt_key = base64.b64decode(bytes(salt_key, 'ascii'))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_key,
        iterations=480000,
    )
    derived_key = kdf.derive(bytes(pw, "ascii"))
    derived_key = base64.b64encode(derived_key).decode('ascii')
    return derived_key


# Genera un salt aleatorio y lo transforma en base 64.
def generar_salt():
    salt = os.urandom(12)
    salt = base64.b64encode(salt).decode('ascii')
    return salt
