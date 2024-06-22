import os
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
from cryptography.x509.oid import NameOID

def generate_passkey(alias, password):
    if os.path.exists(f"{alias}.p12"):
        print("A chave já existe. Pulando a geração.")
        return

    # Gera um par de chaves RSA
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Cria um certificado autoassinado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Sao Paulo"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Sao Paulo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"mycompany.com"),
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        # Nosso certificado será válido por 10 dias
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)
    ).sign(key, hashes.SHA256())

    # Serializa o certificado e a chave privada para PKCS12
    p12_data = pkcs12.serialize_key_and_certificates(
        name=b"clientPasskey",
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
    )

    # Salva o arquivo .p12 no disco
    with open(f"{alias}.p12", "wb") as f:
        f.write(p12_data)

    print("Chave gerada e armazenada no keystore.")

if __name__ == "__main__":
    alias = "clientPasskey"
    password = "password"
    generate_passkey(alias, password)
