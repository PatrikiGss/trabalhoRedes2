import socket               
import threading            
import json                 

class Broker:              
    
    Topico_Clientes = {}    # dicionário que vai armazenar os clientes inscritos em cada tópico

    def Tratando_Cliente(self, conexao, endereco): 
        print(f"Cliente conectado: {endereco}")  # print ao conectar cliente
        while True:                                 
            try:
                dados = conexao.recv(1024).decode()     
                if not dados:                          
                    print(f"Cliente {endereco} desconectou")  # print ao desconectar
                    break
                pacote = json.loads(dados)              
                tipo = pacote.get("type")               

                if tipo == "subscribe" or tipo == "SUBSCRIBE":  
                    topico = pacote["topico"]                   
                    if topico not in self.Topico_Clientes:      
                        self.Topico_Clientes[topico] = []
                    self.Topico_Clientes[topico].append(conexao)  
                    print(f"{endereco} se inscreveu no tópico: {topico}")

                elif tipo == "publish" or tipo == "PUBLISH":
                    topico = pacote["topico"]
                    mensagem = pacote["mensagem"]
                    print(f"Publicação recebida do cliente {endereco} -> tópico: '{topico}', mensagem: '{mensagem}'")  # print da publicação
                    if topico not in self.Topico_Clientes:
                        self.Topico_Clientes[topico] = []
                    for cliente in self.Topico_Clientes[topico]:  
                        try:
                            cliente.sendall(json.dumps({            
                                "topico": topico,
                                "mensagem": mensagem
                            }).encode())                             
                        except (OSError, socket.error):             
                            pass
                elif tipo == "lista":
                    print(f"Cliente {endereco} pediu lista de tópicos")  # print ao pedir lista
                    topicos = list(self.Topico_Clientes.keys())
                    try:
                        conexao.sendall(json.dumps({
                            "type": "lista",
                            "topicos": topicos
                        }).encode())
                    except(OSError, socket.error):
                        pass
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
