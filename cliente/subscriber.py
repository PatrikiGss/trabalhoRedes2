import socket
import json
import threading

class Subscriber:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        topic = input("[SUBSCRIBER] Digite o tópico que deseja assinar: ")
        info = json.dumps({'type': 'SUBSCRIBER', 'topic': topic})
        sock.sendall(info.encode())

        print(f"[SUBSCRIBER] Assinado no tópico '{topic}', aguardando mensagens...\n")
        threading.Thread(target=self.listen, args=(sock,)).start()

    def listen(self, sock):
        while True:
            try:
                data = sock.recv(1024).decode()
                if data:
                    print(f"[MENSAGEM RECEBIDA] {data}")
            except:
                print("[SUBSCRIBER] Conexão encerrada.")
                break


if __name__ == "__main__":
    sub = Subscriber()
    sub.start()
