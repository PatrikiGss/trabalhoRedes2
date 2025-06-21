from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from pathlib import Path

# Caminhos
priv_path = Path("autenticacao/keys/cliente_priv.pem")
csr_path = Path("autenticacao/keys/patriki.csr")

# Carregar a chave privada existente
with open(priv_path, "rb") as f:
    chave_privada = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

# Construir os dados de identidade
nome = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SC"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Lages"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Instituto Federal de Santa Catarina"),
    x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Ciência Da Computação"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Patriki de Oliveira Góss"),
    x509.NameAttribute(NameOID.EMAIL_ADDRESS, "patriki.g2004@aluno.ifsc.edu.br"),
])

# Criar o CSR
csr = (
    x509.CertificateSigningRequestBuilder()
    .subject_name(nome)
    .sign(chave_privada, hashes.SHA256(), default_backend())
)

# Salvar em arquivo .csr (formato PEM)
with open(csr_path, "wb") as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))

print("📄 Requisição de certificado (CSR) gerada com sucesso em:", csr_path)
