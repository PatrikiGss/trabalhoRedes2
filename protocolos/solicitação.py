from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta
from pathlib import Path

# Caminhos
CAMINHO_CHAVE_PRIVADA  = Path("cliente/auth/subscriber_priv.pem")
CAMINHO_CERTIFICADO  = Path("cliente/auth/subscriber.crt")

# 1. Carregar a chave privada
with open(CAMINHO_CHAVE_PRIVADA, "rb") as f:
    chave_privada = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

# 2. Informações do "dono" do certificado
nome = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"São Paulo"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"SistemaMqtt"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Instituto Federal de Santa Catarina"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

# 3. Construção do certificado
certificado = (
    x509.CertificateBuilder()
    .subject_name(nome)
    .issuer_name(nome)  # Autoassinado
    .public_key(chave_privada.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=365))  # 1 ano de validade
    .add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True
    )
    .sign(private_key=chave_privada, algorithm=hashes.SHA256(), backend=default_backend())
)

# 4. Salvar o certificado
with open(CAMINHO_CERTIFICADO, "wb") as f:
    f.write(certificado.public_bytes(serialization.Encoding.PEM))

print(f"✅ Certificado autoassinado gerado em: {CAMINHO_CERTIFICADO}")
