import socket
import threading
import json

class Subscriber:
    def __init__(self, host="localhost", porta=6666):
        self.host = host
        self.porta = porta
        self.escutando = False
        self.mensagens = []

    def escutar(self, topico):
        """Mantém conexão com o broker para escutar mensagens do tópico."""
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
        """Solicita a lista de tópicos ao broker."""
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
        """Publica uma mensagem em um tópico existente."""
        try:
            pacote = {
                "type": "publish",
                "topico": topico,
                "mensagem": mensagem
            }

            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((self.host, self.porta))

            cliente.sendall(json.dumps(pacote).encode())
            cliente.close()
        except Exception as e:
            print(f"[ERRO] Falha ao publicar: {e}")
            self.mensagens.append(f"[ERRO] Falha ao publicar: {e}")
