from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from pathlib import Path

class GerenciadorChaves:
    def __init__(self, pasta="cliente/auth", usuario="subscriber"):
        self.pasta = Path(pasta)
        self.usuario = usuario
        self.priv_path = self.pasta / f"{usuario}_priv.pem"
        self.pub_path = self.pasta / f"{usuario}_pub.pem"
        self.pasta.mkdir(parents=True, exist_ok=True)

        print(f"[DEBUG] GerenciadorChaves inicializado com pasta: {self.pasta}")
        print(f"[DEBUG] Esperando chave privada em: {self.priv_path}")

    def gerar_chave_privada(self):
        chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open(self.priv_path, "wb") as f:
            f.write(chave.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

    def gerar_chave_publica(self):
        with open(self.priv_path, "rb") as f:
            chave = serialization.load_pem_private_key(f.read(), password=None)
        pub = chave.public_key()
        with open(self.pub_path, "wb") as f:
            f.write(pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    def carregar_chave_privada(self):
        with open(self.priv_path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    def carregar_chave_publica(self):
        with open(self.pub_path, "rb") as f:
            return serialization.load_pem_public_key(f.read())
        
    def carregar_certificado(self, caminho_cert="cliente/auth/subscriber.crt"):
        from cryptography import x509
        with open(caminho_cert, "rb") as f:
            return x509.load_pem_x509_certificate(f.read(), default_backend())
