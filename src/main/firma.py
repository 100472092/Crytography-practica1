import os

import cryptography.exceptions
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

DIR_PATH = os.path.dirname(__file__)[:-4]

def generar_claves(path):
    private_key = generate_private()
    save_private_key(private_key, path)
    save_public_key(private_key, path)

def gen_public(path):
    private_key = read_private_key(path)
    save_public_key(private_key, path)

def generate_private():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key

def firmar_fichero(path):
    private_key = read_private_key(DIR_PATH + "keys/")
    sign_data(private_key, path)

def verifica_fichero(file_name):
    #TODO esto hay que cambiarlo a un cert.public_key o algo así de openssl
    public_key = read_private_key(DIR_PATH + "keys/").public_key()
    verify_signature(public_key, file_name)

def read_private_key(path):
    password = bytes(os.environ["key"], "ascii")
    with open(path + "private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=password,
        )
    return private_key


def save_private_key(private_key, path):
    password = bytes(os.environ["key"], "ascii")
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password)
    )
    key_file = path + "private.pem"
    file = os.open(key_file, os.O_CREAT | os.O_RDWR | os.O_TRUNC)
    os.write(file, pem)
    os.close(file)


def save_public_key(private_key, path):
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    key_file = path + "public.pem"
    file = os.open(key_file, os.O_CREAT | os.O_RDWR | os.O_TRUNC)
    os.write(file, pem)
    os.close(file)


def sign_data(private_key, path):
    with open(path, "rb") as message_file:
        message = message_file.read()
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    fichero_firma = os.open(path + ".sig", os.O_CREAT | os.O_RDWR | os.O_TRUNC)
    os.write(fichero_firma, signature)
    os.close(fichero_firma)

def verify_signature(public_key, path):
    with open(path + ".sig", "rb") as signature_file:
        signature = signature_file.read()
    with open(path, "rb") as message_file:
        message = message_file.read()
    try:
        public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
        )
        print("Firma correcta! Fichero es válido")
        return 0
    except cryptography.exceptions.InvalidSignature:
        print("La firma no es correcta")
        return -1


