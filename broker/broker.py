import socket               
import threading            
import json                 

class Broker:              
    
    Topico_Clientes = {}    #este é o dicionario que vai armazenar os clientes inscritos em cada topico

    def Tratando_Cliente(self, conexao, endereco): 
        while True:                                 # Loop para manter a comunicação com o cliente
            try:
                dados = conexao.recv(1024).decode()     # Recebe dados do cliente e decodifica de bytes para string
                if not dados:                          
                    break
                pacote = json.loads(dados)              # Converte a string JSON em dicionário
                tipo = pacote.get("type")               # pega o tipo do pacote (subscribe ou publish)

                if tipo == "subscribe" or tipo == "SUBSCRIBE":  # Verifica se é uma inscrição em tópico
                    topico = pacote["topico"]                   # Obtém o nome do tópico
                    if topico not in self.Topico_Clientes:      # Se o tópico não existe, cria uma lista
                        self.Topico_Clientes[topico] = []
                    self.Topico_Clientes[topico].append(conexao)  # Adiciona a conexão à lista de inscritos
                    print(f"{endereco} se inscreveu no topico: {topico}")  # Mensagem de confirmação no servidor

                elif tipo == "publish" or tipo == "PUBLISH":     # Verifica se é uma publicação em tópico
                    topico = pacote["topico"]                    # Obtém o nome do tópico
                    mensagem = pacote["message"]                 # Obtém a mensagem a ser publicada
                    for cliente in self.Topico_Clientes.get(topico, []):  # Envia para todos os clientes inscritos
                        try:
                            cliente.sendall(json.dumps({            # Envia a mensagem em formato JSON
                                "topico": topico,
                                "mensagem": mensagem
                            }).encode())                             # Codifica para bytes antes de enviar
                        except (OSError, socket.error):             # Ignora erros de envio
                            pass
            except (json.JSONDecodeError, ConnectionResetError, OSError):  # Trata erros comuns de conexão/JSON
                break
        conexao.close()     

    def Iniciando_Broker(self):      
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        servidor.bind(("localhost", 5050))         
        servidor.listen()                          
        print("servidor aguardando conexoes na porta 5050...")  

        while True:                                # Loop infinito para aceitar novas conexões
            conexao, endereco = servidor.accept()  # Aceita uma nova conexão e obtém o endereço do cliente
            threading.Thread(target=self.Tratando_Cliente, args=(conexao, endereco)).start()  # Inicia uma nova thread para lidar com o cliente

if __name__ == "__main__":  
    broker = Broker()       
    broker.Iniciando_Broker()  
                              
"""
socket.AF_INET → Endereço IP no padrão IPv4

socket.SOCK_STREAM → Tipo de conexão (TCP)

socket.socket() → Cria um novo socket

bind() → Diz onde o servidor vai “ficar ouvindo”

listen() → Começa a escutar pedidos de conexão

accept() → Espera alguém conectar (bloqueia até isso acontecer)

recv() → Recebe dados enviados pelo cliente

sendall() → Envia todos os dados codificados para o cliente

decode() → Converte de bytes para string

encode() → Converte de string para bytes

json.loads() → Converte string JSON em dicionário

json.dumps() → Converte dicionário para string JSON

threading.Thread() → Cria uma nova thread para execução paralela

start() → Inicia a thread criada

close() → Fecha o socket
"""
