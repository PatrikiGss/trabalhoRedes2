import socket
import threading
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from protocolos.envelopamento import Envelopador
from broker.auth.chaves import GerenciadorChaves
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from pathlib import Path

class Subscriber:
    def __init__(self, host="localhost", porta=6666):
        self.host = host
        self.porta = porta
        self.escutando = False
        self.mensagens = []

    def escutar(self, topico):
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((self.host, self.porta))

            mensagem_sub = {
                "type": "subscribe",
                "topico": topico
            }
            cliente.sendall(json.dumps(mensagem_sub).encode())

            self.escutando = True
            print(f"Inscrito no tópico '{topico}'. Aguardando mensagens...")

            while True:
                dados = cliente.recv(1024).decode()
                if not dados:
                    print("Conexão encerrada pelo servidor.")
                    break
                pacote = json.loads(dados)
                topico_recv = pacote.get("topico", "N/A")
                mensagem = pacote.get("mensagem", "Sem mensagem")
                print(f"[{topico_recv}] {mensagem}")
                self.mensagens.append(f"[{topico_recv}] {mensagem}")
        except Exception as e:
            print(f"[ERRO] Falha ao escutar mensagens: {e}")
            self.mensagens.append(f"[ERRO] {e}")

    def iniciar_escuta(self, topico):
        if not self.escutando:
            threading.Thread(target=self.escutar, args=(topico,), daemon=True).start()
            self.escutando = True

    def ListaTopicos(self):
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((self.host, self.porta))

            pedido = {"type": "lista"}
            cliente.sendall(json.dumps(pedido).encode())

            dados = cliente.recv(1024).decode()
            cliente.close()

            resposta = json.loads(dados)
            if resposta.get("type") == "lista":
                return resposta.get("topicos", [])
            else:
                return []
        except Exception as e:
            print(f"[ERRO] Falha ao obter lista de tópicos: {e}")
            return []

    def publish(self, topico, mensagem):
        try:
            chave_sim = os.urandom(32)
            mensagem_bytes = mensagem.encode("utf-8")
            mensagem_criptografada = Envelopador.criptografar_mensagem(mensagem_bytes, chave_sim)
            cert_path = Path(__file__).resolve().parent.parent / "broker" / "auth" / "broker.crt"
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read(), default_backend())
                chave_pub_broker = cert.public_key()

            chave_sim_cript = Envelopador.criptografar_chave_simetrica(chave_sim, chave_pub_broker)

            pacote = {
                "type": "publish",
                "topico": topico,
                "mensagem": mensagem_criptografada,
                "chave_simetrica": chave_sim_cript
            }

            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((self.host, self.porta))
            cliente.sendall(json.dumps(pacote).encode("utf-8"))
            cliente.close()

        except Exception as e:
            print(f"[ERRO] Falha ao publicar criptografado: {e}")
            self.mensagens.append(f"[ERRO] Falha ao publicar criptografado: {e}")
