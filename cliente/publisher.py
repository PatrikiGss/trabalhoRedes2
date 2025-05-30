import socket                 
import json                  

while True: 
             
    topico = input("Insira o tópico: ")            
    mensagem = input("Insira a mensagem: ")        
    pacote = {                                     # Cria um dicionário com os dados da publicação
        "type": "publish",                         # Tipo da mensagem (publicação)
        "topico": topico,                          # Tópico para o qual a mensagem será enviada
        "mensagem": mensagem                       # Conteúdo da mensagem
    }
    lista_de_topicos=[topico]
    print(f"topicos existentes: {topico}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    s.connect(("localhost", 6666))                

    pacote_json = json.dumps(pacote)              # Converte o dicionário em uma string JSON

    pacote_bytes = pacote_json.encode("utf-8")    # Codifica a string JSON para bytes (necessário para enviar pelo socket)
    s.sendall(pacote_bytes)                       # Envia os bytes para o broker
    print(f"Mensagem publicada no tópico {topico}: {mensagem}")  

    s.close()                                  

    sair = input("Deseja enviar outra mensagem? (s/n): ") 
    if sair.lower() != 's':                       
        break
