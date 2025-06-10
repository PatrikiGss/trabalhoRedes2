import socket
import json


def publicar_topico(topico: str, host="localhost", porta=6666):
    try:
        pacote = {
            "type": "publish",
            "topico": topico,
            
        }

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((host, porta))

        # Serializa para JSON e converte em bytes
        pacote_json = json.dumps(pacote)
        pacote_bytes = pacote_json.encode("utf-8")

        # Envia os dados
        s.sendall(pacote_bytes)

        s.close()

        return f"Tópico publicado:  {topico}"

    except Exception as e:
        return f"Erro ao publicar topico: {e}"   
