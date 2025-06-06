import socket
import json


def publicar_mensagem(topico: str, mensagem: str, host="localhost", porta=6666):

    try:
        pacote = {
            "type": "publish",
            "topico": topico,
            "mensagem": mensagem
        }

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((host, porta))

        # Serializa para JSON e converte em bytes
        pacote_json = json.dumps(pacote)
        pacote_bytes = pacote_json.encode("utf-8")

        # Envia os dados
        s.sendall(pacote_bytes)

        s.close()

        return f"✅ Mensagem publicada no tópico '{topico}': {mensagem}"

    except Exception as e:
        return f"❌ Erro ao publicar mensagem: {e}"   
"""
    Publica uma mensagem em um tópico específico no broker via TCP.

    Parâmetros:
    - topico (str): O nome do tópico.
    - mensagem (str): O conteúdo da mensagem.
    - host (str): Endereço do broker (padrão: localhost).
    - porta (int): Porta do broker (padrão: 6666).

    Retorno:
    - str: Mensagem de confirmação ou erro.
"""
