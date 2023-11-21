import os

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from cryptography.x509.oid import NameOID

DIR_PATH = os.path.dirname(__file__)[:-4]

def generar_claves(path):
    private_key = generate_private()
    save_private_key(private_key, path)
    save_public_key(private_key, path)
    create_csr(private_key)

def gen_public(path):
    private_key = read_private_key(path)
    save_public_key(private_key, path)
    create_csr(private_key)

def generate_private():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key

def firmar_fichero(path):
    private_key = read_private_key(DIR_PATH + "keys/")
    sign_data(private_key, path)

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
    fichero_firma = os.open(path[:-4] + ".sig", os.O_CREAT | os.O_RDWR | os.O_TRUNC)
    os.write(fichero_firma, signature)
    os.close(fichero_firma)


def create_csr(private_key):
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "MADRID"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "LEGANES"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "UC3M"),
    x509.NameAttribute(NameOID.COMMON_NAME, "72092"),
    ])).add_extension(
        x509.SubjectAlternativeName([]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    with open("../../OpenSSL/AC1/solicitudes/A_csr.pem", "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))