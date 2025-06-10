import socket
import threading
import json

class Subscriber:
    def __init__(self):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect(("localhost", 6666))
        self.topico = None
        self.mensagem = None
        self.mensagens = []
        self.escutando = False

    def escutar(self):
        """Escuta mensagens dos tópicos inscritos."""
        while True:
            try:
                dados = self.cliente.recv(1024).decode()
                if not dados:
                    print("Conexão encerrada pelo servidor.")
                    break
                pacote = json.loads(dados)
                topico = pacote.get("topico", "N/A")
                mensagem = pacote.get("mensagem", "Sem mensagem")
                self.mensagens.append(f"[{topico}] {mensagem}")
            except Exception as e:
                self.mensagens.append(f"[ERRO] {e}")
                break

    def ListaTopicos(self):
        """Solicita a lista de tópicos disponíveis no broker."""
        try:
            pedido = {"type": "lista"}
            self.cliente.sendall(json.dumps(pedido).encode())
            dados = self.cliente.recv(1024).decode()
            resposta = json.loads(dados)
            if resposta.get("type") == "lista":
                return resposta.get("topicos", [])
        except:
            return []
        return []

    def subscribe(self, topico, mensagem="Inscrição confirmada"):
        """Envia requisição de inscrição a um tópico."""
        self.topico = topico
        self.mensagem = mensagem
        mensagem_sub = {
            "type": "subscribe",
            "topico": self.topico,
            "mensagem": self.mensagem
        }
        try:
            self.cliente.sendall(json.dumps(mensagem_sub).encode())
        except Exception as e:
            self.mensagens.append(f"[ERRO] Falha ao se inscrever: {e}")
        if not self.escutando:
            threading.Thread(target=self.escutar, daemon=True).start()
            self.escutando = True
