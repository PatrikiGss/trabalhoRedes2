import socket
import json

def criar_topico(topico: str, host="localhost", porta=6666):
    try:
        pacote = {
            "type": "publisher",
            "topico": topico
        }

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, porta))

        pacote_json = json.dumps(pacote)
        s.sendall(pacote_json.encode("utf-8"))

        s.close()

        return f"Tópico '{topico}' criado com sucesso."

    except Exception as e:
        return f"Erro ao criar tópico: {e}"
