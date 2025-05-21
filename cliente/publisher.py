import socket
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 6666))

pacote = {
    "type": "publish",
    "topico": "noticias",
    "mensagem": "Olá, mundo!"
}

s.sendall(json.dumps(pacote).encode())
s.close()
