
import cryptography.exceptions
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509


def verify_all(path):
    AC1_cert = abrir_certificado("../../OpenSSL/AC1/ac1cert.pem")
    A_cert = abrir_certificado("../../OpenSSL/A/Acert.pem")
    public_key_autoridad = AC1_cert.public_key()
    verify_certificate(public_key_autoridad, AC1_cert)
    public_key_sistema = A_cert.public_key()
    verify_certificate(public_key_autoridad, A_cert)
    verify_signature(public_key_sistema, path)


def verify_certificate(clave_autoridad, cert):
    try:
        clave_autoridad.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
        print("El certificado es válido")
        return 0
    except cryptography.exceptions.InvalidSignature:
        print("El certificado no es válido")
        return -1

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


def abrir_certificado(path):
    with open(path, "rb") as certificado:
        certificado = certificado.read()

    cert = x509.load_pem_x509_certificate(certificado)

    return cert