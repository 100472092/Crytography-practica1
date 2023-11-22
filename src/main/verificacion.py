import os.path

import cryptography.exceptions
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509

PATH = os.path.dirname(__file__)[:-8]


def verify_all(path_fichero, path_firma, root_cert, sys_cert):
    AC1_cert = abrir_certificado(root_cert)
    if AC1_cert == -1:
        return -1
    A_cert = abrir_certificado(sys_cert)
    if A_cert == -1:
        return -2

    public_key_autoridad = AC1_cert.public_key()
    if verify_certificate(public_key_autoridad, A_cert) == -1:
        return -3
    if verify_certificate(public_key_autoridad, AC1_cert) == -1:
        return -4
    public_key_sistema = A_cert.public_key()
    if verify_signature(public_key_sistema, path_firma, path_fichero) == -1:
        return -5


def verify_certificate(clave_autoridad, cert):
    try:
        clave_autoridad.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
        print("El certificado es válido, Data: " + str(cert.subject))
        return 0
    except cryptography.exceptions.InvalidSignature:
        print("El certificado no es válido")
        return -1


def verify_signature(public_key, path_firma, path_archivo):
    with open(path_firma, "rb") as signature_file:
        signature = signature_file.read()
    with open(path_archivo, "rb") as message_file:
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


def abrir_certificado(path):
    try:
        with open(path, "rb") as certificado:
            certificado = certificado.read()
        cert = x509.load_pem_x509_certificate(certificado)
        return cert
    except:
        print("Certificado defectuoso o modificado")
        return -1
