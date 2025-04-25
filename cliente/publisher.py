import socket
import json

class Publisher:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        topic = input("[PUBLISHER] Digite o nome do tópico para publicar: ")
        info = json.dumps({'type': 'PUBLISHER', 'topic': topic})
        sock.sendall(info.encode())
        return sock, topic

    def publish(self, sock, topic):
        while True:
            msg = input(f"[PUBLISHER][{topic}] Digite a mensagem: ")
            if msg.lower() == 'sair':
                print("[PUBLISHER] Encerrando conexão.")
                sock.close()
                break
            sock.sendall(msg.encode())


if __name__ == "__main__":
    pub = Publisher()
    conn, topic = pub.start()
    pub.publish(conn, topic)
