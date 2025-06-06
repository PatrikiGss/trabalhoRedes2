import socket       
import threading    
import json          

class Subscriber:
    def __init__(self):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect(("localhost", 6666))
        self.topico = None
        self.mensagens=[]
        
    def escutar(self):
        """Escuta mensagens dos tópicos inscritos."""
        while True:
            try:
                dados = self.cliente.recv(1024).decode()
                if not dados:
                    print("Conexão encerrada pelo servidor.")
                    break
                pacote = json.loads(dados)
                self.mensagens.append(f"[{pacote['topico']}] {pacote['mensagem']}")
            except Exception as e:
                self.mensagens.append(f"[ERRO] {e}")
                break

    def ListaTopicos(self):
        """Solicita a lista de tópicos disponíveis no broker."""
        pedido = {"type": "lista"}
        self.cliente.sendall(json.dumps(pedido).encode())
        dados = self.cliente.recv(1024).decode()
        # Converte o JSON recebido em um dicionário Python
        resposta = json.loads(dados)
        # Se o tipo for 'lista', retorna a lista de tópicos
        if resposta.get("type") == "lista":
            return resposta.get("topicos", [])
        return []

    def subscribe(self, topico):
        """Envia requisição de inscrição a um tópico."""
        # Define o tópico atual (sobrescrevendo qualquer anterior)
        self.topico = topico
        mensagem_sub = {
            "type": "subscribe",
            "topico": self.topico
        }
        self.cliente.sendall(json.dumps(mensagem_sub).encode())
        threading.Thread(target=self.escutar, daemon=True).start()

"""   def iniciar(self):
        while True:
            # Pega a lista de tópicos disponíveis no broker
            topicos = self.ListaTopicos()

            # Mostra os tópicos disponíveis para o usuário
            if topicos:
                print("\n📜 Tópicos disponíveis no broker:")
                for idx, t in enumerate(topicos):
                    print(f"{idx + 1} - {t}")
            else:
                print("\n❌ Nenhum tópico disponível no momento.")

            # Pergunta ao usuário o número do tópico ou um novo nome
            opcao = input("\nDigite o número do tópico para se inscrever ou digite um novo nome para criar um tópico: ")

            # Verifica se a entrada é um número correspondente a um tópico existente
            if opcao.isdigit() and 1 <= int(opcao) <= len(topicos):
                topico_escolhido = topicos[int(opcao) - 1]  # Seleciona da lista
            else:
                topico_escolhido = opcao.strip()  # Usa como novo tópico

            # Faz a inscrição no tópico selecionado ou criado
            self.subscribe(topico_escolhido)
            input("\n🔔 Aguardando mensagens... Pressione Enter para se inscrever em outro tópico.\n")

if __name__ == "__main__":
    sub = Subscriber()
    sub.iniciar()
"""