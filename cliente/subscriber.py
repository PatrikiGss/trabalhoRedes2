import socket
import threading
import json

class Subscriber:
    def __init__(self, topico="bdg3"):
        self.topico = topico
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect(("localhost", 6666))
        self.subscribe()

    def escutar(self):
        while True:
            try:
                dados = self.cliente.recv(1024).decode()
                if not dados:
                    print("Conexão encerrada pelo servidor.")
                    break
                pacote = json.loads(dados)
                print(f"Mensagem recebida do tópico '{pacote['topico']}': {pacote['mensagem']}")
            except Exception as e:
                print(f"Erro ao receber dados: {e}")
                break

    def subscribe(self):
        mensagem_sub = {
            "type": "subscribe",
            "topico": self.topico
        }
        self.cliente.sendall(json.dumps(mensagem_sub).encode())
        print(f"Inscrito no tópico: {self.topico}")
        threading.Thread(target=self.escutar, daemon=True).start()

if __name__ == "__main__":
    sub = Subscriber(topico="bdg3")
    input("Aguardando mensagens... Pressione Enter para sair.\n")
