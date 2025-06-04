import socket       
import threading    
import json          

class Subscriber:
    def __init__(self):
        """Inicializa o assinante e conecta ao broker."""
        # Cria um socket TCP
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Faz conexão com o broker no endereço 'localhost' e porta 6666
        self.cliente.connect(("localhost", 6666))
        # Armazena o tópico atual (nesse modelo, só um por vez)
        self.topico = None
        # Aqui poderia iniciar diretamente a inscrição, mas está comentado
        # self.subscribe()
        
    def escutar(self):
        """Escuta mensagens dos tópicos inscritos."""
        while True:
            try:
                # Aguarda a chegada de dados do broker
                dados = self.cliente.recv(1024).decode()

                # Se não recebeu nada, provavelmente a conexão foi encerrada
                if not dados:
                    print("Conexão encerrada pelo servidor.")
                    break

                # Converte os dados JSON em um dicionário
                pacote = json.loads(dados)

                # Exibe a mensagem recebida, mostrando de qual tópico veio
                print(f"Mensagem recebida do tópico '{pacote['topico']}': {pacote['mensagem']}")

            except Exception as e:
                # Caso aconteça algum erro na recepção
                print(f"Erro ao receber dados: {e}")
                break

    def ListaTopicos(self):
        """Solicita a lista de tópicos disponíveis no broker."""
        pedido = {
            "type": "lista"
        }
        # Envia o pedido para o broker
        self.cliente.sendall(json.dumps(pedido).encode())
        dados = self.cliente.recv(1024).decode()
        # Converte o JSON recebido em um dicionário Python
        resposta = json.loads(dados)
        # Se o tipo for 'lista', retorna a lista de tópicos
        if resposta.get("type") == "lista":
            return resposta.get("topicos", [])
        
        # Caso não seja uma resposta válida, retorna lista vazia
        return []

    def subscribe(self, topico):
        """Envia requisição de inscrição a um tópico."""
        # Define o tópico atual (sobrescrevendo qualquer anterior)
        self.topico = topico

        # Monta a mensagem de inscrição no formato JSON
        mensagem_sub = {
            "type": "subscribe",
            "topico": self.topico
        }

        # Envia a mensagem de inscrição para o broker
        self.cliente.sendall(json.dumps(mensagem_sub).encode())

        # Confirma no terminal que a inscrição foi feita
        print(f"Inscrito no tópico: {self.topico}")

        # Inicia uma nova thread que executa a função escutar()
        threading.Thread(target=self.escutar, daemon=True).start()

    def iniciar(self):
        """Menu interativo para o usuário escolher tópicos."""
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
