from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes
import os, base64

class Envelopador:
    @staticmethod
    def criptografar_mensagem(mensagem_bytes, chave_simetrica):
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(mensagem_bytes) + padder.finalize()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(chave_simetrica), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + ciphertext).decode()

    @staticmethod
    def descriptografar_mensagem(cipher_base64, chave_simetrica):
        dados = base64.b64decode(cipher_base64)
        iv = dados[:16]
        ciphertext = dados[16:]
        cipher = Cipher(algorithms.AES(chave_simetrica), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()

    @staticmethod
    def criptografar_chave_simetrica(chave_sim, chave_publica_destino):
        return base64.b64encode(
            chave_publica_destino.encrypt(
                chave_sim,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        ).decode()

    @staticmethod
    def descriptografar_chave_simetrica(chave_cript_base64, chave_privada):
        chave_cript = base64.b64decode(chave_cript_base64)
        return chave_privada.decrypt(
            chave_cript,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    @staticmethod
    def gerar_chave_simetrica(tamanho=32):  # 32 bytes = 256 bits
        return os.urandom(tamanho)
