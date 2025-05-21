import socket               
import threading           
import json                

class Broker:              
    
    Topico_Clientes = {}    

    def Tratando_Cliente(self, conexao, endereco): 
        print(f"Cliente conectado: {endereco}")     # Exibe o IP/porta do cliente que se conectou
        while True:                                 # Loop contínuo para manter o atendimento do cliente
            try:
                dados = conexao.recv(1024).decode()     # Recebe até 1024 bytes do cliente e decodifica de bytes para string
                if not dados:                           # Se não houver dados, significa que o cliente desconectou
                    print(f"Cliente {endereco} desconectou")  # Informa a desconexão
                    break
                pacote = json.loads(dados)              # Converte a string JSON recebida para um dicionário Python
                tipo = pacote.get("type")               # Obtém o tipo de operação (subscribe, publish ou lista)

                if tipo == "subscribe" or tipo == "SUBSCRIBE":  # Se o cliente quer se inscrever em um tópico
                    topico = pacote["topico"]                   # Obtém o nome do tópico
                    if topico not in self.Topico_Clientes:      # Se o tópico ainda não existe no dicionário
                        self.Topico_Clientes[topico] = []       # Cria uma lista vazia para os clientes do tópico
                    self.Topico_Clientes[topico].append(conexao)  # Adiciona a conexão do cliente à lista do tópico
                    print(f"{endereco} se inscreveu no tópico: {topico}")  # Informa a inscrição no tópico

                elif tipo == "publish" or tipo == "PUBLISH":    # Se o cliente quer publicar uma mensagem
                    topico = pacote["topico"]                   # Obtém o nome do tópico
                    mensagem = pacote["mensagem"]               # Obtém a mensagem a ser publicada
                    print(f"Publicação recebida do cliente {endereco} -> tópico: '{topico}', mensagem: '{mensagem}'")  # Log da publicação
                    if topico not in self.Topico_Clientes:      # Se ninguém está inscrito nesse tópico
                        self.Topico_Clientes[topico] = []       # Cria a lista (mesmo que vazia)
                    for cliente in self.Topico_Clientes[topico]:  # Para cada cliente inscrito no tópico
                        try:
                            cliente.sendall(json.dumps({            # Envia a mensagem para o cliente
                                "topico": topico,                   # Inclui o nome do tópico
                                "mensagem": mensagem                # Inclui a mensagem publicada
                            }).encode())                            # Codifica como bytes antes de enviar
                        except (OSError, socket.error):             # Em caso de erro ao enviar (cliente desconectado, etc.)
                            pass                                    # Ignora e segue para o próximo cliente

                elif tipo == "lista":                               # Se o cliente solicitou a lista de tópicos
                    print(f"Cliente {endereco} pediu lista de tópicos")  # Log da solicitação
                    topicos = list(self.Topico_Clientes.keys())          # Cria uma lista com todos os nomes de tópicos
                    try:
                        conexao.sendall(json.dumps({                    # Envia a lista de tópicos para o cliente
                            "type": "lista",                           # Tipo da mensagem de resposta
                            "topicos": topicos                         # Lista de tópicos
                        }).encode())                                   # Codifica como bytes
                    except(OSError, socket.error):                     # Se der erro ao enviar, ignora
                        pass
            except (json.JSONDecodeError, ConnectionResetError, OSError):  # Se o cliente enviar dados inválidos ou cair a conexão
                print(f"Erro ou desconexão do cliente {endereco}")        # Log do erro
                break
        conexao.close()      

    def Iniciando_Broker(self):       
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        servidor.bind(("localhost", 6666))        
        servidor.listen()                          
        print("Servidor aguardando conexões na porta 6666...")  

        while True:                                
            conexao, endereco = servidor.accept()  
            threading.Thread(target=self.Tratando_Cliente, args=(conexao, endereco)).start()  # Cria e inicia uma nova thread para esse cliente

if __name__ == "__main__":   
    broker = Broker()        
    broker.Iniciando_Broker()  
