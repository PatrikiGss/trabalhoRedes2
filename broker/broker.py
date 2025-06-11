import socket
import threading
import json

class Broker:
    def __init__(self):
        self.Topicos_Criados = set()            # Tópicos criados por publishers
        self.Topico_Clientes = {}               # { topico: [conexoes inscritas] }

    def Tratando_Cliente(self, conexao, endereco):
        print(f"Cliente conectado: {endereco}")
        while True:
            try:
                dados = conexao.recv(1024).decode()
                if not dados:
                    print(f"Cliente {endereco} desconectou")
                    break

                pacote = json.loads(dados)
                tipo = pacote.get("type").lower()

                if tipo == "publisher":
                    topico = pacote.get("topico")
                    if topico:
                        if topico not in self.Topicos_Criados:
                            self.Topicos_Criados.add(topico)
                            self.Topico_Clientes[topico] = []
                            print(f"Tópico criado por {endereco}: '{topico}'")
                        else:
                            print(f"Tópico já existente: '{topico}' (solicitado por {endereco})")
                    conexao.close()
                    break

                elif tipo == "subscribe":
                    topico = pacote.get("topico")
                    if topico in self.Topicos_Criados:
                        if conexao not in self.Topico_Clientes[topico]:
                            self.Topico_Clientes[topico].append(conexao)
                            print(f"{endereco} se inscreveu no tópico: '{topico}'")
                        else:
                            print(f"{endereco} já está inscrito no tópico: '{topico}'")
                    else:
                        conexao.sendall(json.dumps({
                            "erro": f"Tópico '{topico}' não existe. Crie-o com um publisher antes."
                        }).encode())

                elif tipo == "publish":
                    topico = pacote.get("topico")
                    mensagem = pacote.get("mensagem")
                    if topico in self.Topicos_Criados:
                        print(f"Mensagem publicada por {endereco} -> tópico: '{topico}', mensagem: '{mensagem}'")
                        for cliente in self.Topico_Clientes.get(topico, []):
                            try:
                                cliente.sendall(json.dumps({
                                    "topico": topico,
                                    "mensagem": mensagem
                                }).encode())
                            except (OSError, socket.error):
                                pass
                    else:
                        conexao.sendall(json.dumps({
                            "erro": f"Tópico '{topico}' não existe. Não é possível publicar."
                        }).encode())

                elif tipo == "lista":
                    print(f"Cliente {endereco} pediu lista de tópicos")
                    conexao.sendall(json.dumps({
                        "type": "lista",
                        "topicos": list(self.Topicos_Criados)
                    }).encode())

            except (json.JSONDecodeError, ConnectionResetError, OSError):
                print(f"Erro ou desconexão do cliente {endereco}")
                break

        conexao.close()

    def Iniciando_Broker(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind(("localhost", 6666))
        servidor.listen()
        print("Servidor aguardando conexões na porta 6666...")

        while True:
            conexao, endereco = servidor.accept()
            threading.Thread(target=self.Tratando_Cliente, args=(conexao, endereco)).start()

if __name__ == "__main__":
    broker = Broker()
    broker.Iniciando_Broker()
