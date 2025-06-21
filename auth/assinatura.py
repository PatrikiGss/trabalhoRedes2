from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

class AssinadorDigital:
    @staticmethod
    def assinar(mensagem_bytes, chave_privada):
        assinatura = chave_privada.sign(
            mensagem_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(assinatura).decode()

    @staticmethod
    def verificar(mensagem_bytes, assinatura_base64, chave_publica):
        assinatura = base64.b64decode(assinatura_base64)
        from cryptography.exceptions import InvalidSignature
        try:
            chave_publica.verify(
                assinatura,
                mensagem_bytes,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
