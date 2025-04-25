import socket
import threading
import json

class Broker:
    def __init__(self, host='localhost', port=5000):
        self.topics = {}
        self.lock = threading.Lock()
        self.host = host
        self.port = port

    def start(self):
        print(f"[BROKER] Iniciando servidor em {self.host}:{self.port}...")
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()
            print("[BROKER] Servidor ouvindo por conexões...")
        except Exception as e:
            print(f"[ERRO] Falha ao iniciar o broker: {e}")
            return

        while True:
            try:
                conn, addr = server.accept()
                print(f"[BROKER] Nova conexão recebida de {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except Exception as e:
                print(f"[ERRO] Erro ao aceitar conexão: {e}")

    def handle_client(self, conn, addr):
        try:
            data = conn.recv(1024).decode()
            if not data:
                print(f"[AVISO] Conexão vazia de {addr}")
                conn.close()
                return

            info = json.loads(data)
            client_type = info.get('type')
            topic = info.get('topic')

            if client_type == 'SUBSCRIBER':
                self.register_subscriber(conn, topic)
            elif client_type == 'PUBLISHER':
                self.handle_publisher(conn, topic)
            else:
                print(f"[ERRO] Tipo de cliente desconhecido: {client_type}")
                conn.close()
        except json.JSONDecodeError:
            print(f"[ERRO] JSON inválido recebido de {addr}")
            conn.close()
        except Exception as e:
            print(f"[ERRO] Falha ao lidar com cliente {addr}: {e}")
            conn.close()

    def register_subscriber(self, conn, topic):
        print(f"[BROKER] Registrando assinante no tópico '{topic}'")
        with self.lock:
            if topic not in self.topics:
                self.topics[topic] = []
            self.topics[topic].append(conn)

        try:
            while True:
                data = conn.recv(1)  # só pra manter a conexão viva
                if not data:
                    break
        except Exception as e:
            print(f"[BROKER] Assinante de {topic} desconectado ({e})")
        finally:
            with self.lock:
                if topic in self.topics and conn in self.topics[topic]:
                    self.topics[topic].remove(conn)
            conn.close()

    def handle_publisher(self, conn, topic):
        print(f"[BROKER] Publisher conectado ao tópico '{topic}'")
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    print(f"[BROKER] Publisher do tópico '{topic}' desconectado.")
                    break
                print(f"[BROKER] Publicando mensagem no tópico '{topic}': {data}")
                self.publish(topic, data)
            except Exception as e:
                print(f"[BROKER] Erro com publisher de '{topic}': {e}")
                break
        conn.close()

    def publish(self, topic, message):
        with self.lock:
            subscribers = self.topics.get(topic, []).copy()

        for subscriber in subscribers:
            try:
                subscriber.sendall(message.encode())
            except Exception as e:
                print(f"[BROKER] Falha ao enviar para assinante de '{topic}': {e}")
                with self.lock:
                    self.topics[topic].remove(subscriber)

if __name__ == "__main__":
    broker = Broker()
    broker.start()
