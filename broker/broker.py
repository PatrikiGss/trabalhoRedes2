from datetime import datetime
import socket
import threading
import json
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from broker.auth.chaves import GerenciadorChaves
from broker.auth.assinatura import AssinadorDigital
from protocolos.envelopamento import Envelopador
from pathlib import Path
import base64


class Broker:
    def __init__(self):
        self.Topicos_Criados = set()
        self.Topico_Clientes = {}
        self.Topico_UltimaMensagem = {}
        self.gerenciador_chaves = GerenciadorChaves()
        self.chave_privada = self.gerenciador_chaves.carregar_chave_privada()
        self.certificado_pem = self.gerenciador_chaves.carregar_certificado()
        caminho_cert = Path("broker/auth/broker.crt")
        self.certificado_pem = caminho_cert.read_text()

    def _get_current_timestamp(self):
        return datetime.now().isoformat()

    def _enviar_resposta(self, conexao, dados):
        dados['server_timestamp'] = self._get_current_timestamp()
        try:
            conexao.sendall(json.dumps(dados).encode())
        except (OSError, socket.error):
            pass

    def Tratando_Cliente(self, conexao, endereco):
        print(f"[{self._get_current_timestamp()}] Cliente conectado: {endereco}")
        while True:
            try:
                dados = conexao.recv(1024).decode()
                if not dados:
                    print(f"[{self._get_current_timestamp()}] Cliente {endereco} desconectou")
                    break

                pacote = json.loads(dados)
                pacote['client_timestamp'] = pacote.get('timestamp', self._get_current_timestamp())
                tipo = pacote.get("type").lower()

                if tipo == "publisher":
                    topico = pacote.get("topico")
                    if topico:
                        if topico not in self.Topicos_Criados:
                            self.Topicos_Criados.add(topico)
                            self.Topico_Clientes[topico] = []
                            self.Topico_UltimaMensagem[topico] = {
                                'mensagem': None,
                                'timestamp': None,
                                'publisher': str(endereco)
                            }
                            print(f"[{self._get_current_timestamp()}] Tópico criado por {endereco}: '{topico}'")
                            self._enviar_resposta(conexao, {
                                "status": "success",
                                "message": f"Tópico '{topico}' criado com sucesso"
                            })
                        else:
                            print(f"[{self._get_current_timestamp()}] Tópico já existente: '{topico}'")
                            self._enviar_resposta(conexao, {
                                "status": "info",
                                "message": f"Tópico '{topico}' já existe"
                            })
                    conexao.close()
                    break

                elif tipo == "subscribe":
                    topico = pacote.get("topico")
                    if topico in self.Topicos_Criados:
                        if conexao not in self.Topico_Clientes[topico]:
                            self.Topico_Clientes[topico].append(conexao)
                            print(f"[{self._get_current_timestamp()}] {endereco} se inscreveu no tópico: '{topico}'")

                            if self.Topico_UltimaMensagem[topico]['mensagem']:
                                self._enviar_resposta(conexao, {
                                    "type": "last_message",
                                    "topico": topico,
                                    "mensagem": self.Topico_UltimaMensagem[topico]['mensagem'],
                                    "original_timestamp": self.Topico_UltimaMensagem[topico]['timestamp'],
                                    "publisher": self.Topico_UltimaMensagem[topico]['publisher']
                                })
                        else:
                            print(f"[{self._get_current_timestamp()}] {endereco} já está inscrito no tópico: '{topico}'")
                            self._enviar_resposta(conexao, {
                                "status": "info",
                                "message": f"Você já está inscrito no tópico '{topico}'"
                            })
                    else:
                        self._enviar_resposta(conexao, {
                            "status": "error",
                            "erro": f"Tópico '{topico}' não existe. Crie-o com um publisher antes."
                        })

                elif tipo == "publish":
                    topico = pacote.get("topico")
                    mensagem_criptografada = pacote.get("mensagem")
                    chave_sim_cript = pacote.get("chave_simetrica")

                    if topico in self.Topicos_Criados:
                        try:
                            from broker.auth.chaves import GerenciadorChaves
                            from protocolos.envelopamento import Envelopador

                            gerador = GerenciadorChaves(usuario="broker")
                            chave_privada = gerador.carregar_chave_privada()

                            chave_sim = Envelopador.descriptografar_chave_simetrica(chave_sim_cript, chave_privada)
                            mensagem_bytes = Envelopador.descriptografar_mensagem(mensagem_criptografada, chave_sim)
                            mensagem = mensagem_bytes.decode("utf-8")

                            timestamp = self._get_current_timestamp()
                            print(f"[{timestamp}] Mensagem criptografada recebida de {endereco} -> tópico: '{topico}'")

                            self.Topico_UltimaMensagem[topico] = {
                                'mensagem': mensagem,
                                'timestamp': timestamp,
                                'publisher': str(endereco)
                            }

                            mensagem_completa = {
                                "type": "message",
                                "topico": topico,
                                "mensagem": mensagem,
                                "publish_timestamp": timestamp,
                                "publisher": str(endereco),
                                "server_timestamp": self._get_current_timestamp()
                            }

                            for cliente in self.Topico_Clientes.get(topico, []):
                                try:
                                    cliente.sendall(json.dumps(mensagem_completa).encode())
                                except (OSError, socket.error):
                                    self.Topico_Clientes[topico].remove(cliente)

                        except Exception as e:
                            print(f"[ERRO] Falha ao processar mensagem criptografada: {e}")
                            self._enviar_resposta(conexao, {
                                "status": "error",
                                "erro": f"Erro ao processar mensagem criptografada: {str(e)}"
                            })
                    else:
                        self._enviar_resposta(conexao, {
                            "status": "error",
                            "erro": f"Tópico '{topico}' não existe. Não é possível publicar."
                        })

                elif tipo == "lista":
                    print(f"[{self._get_current_timestamp()}] Cliente {endereco} pediu lista de tópicos")
                    self._enviar_resposta(conexao, {
                        "type": "lista",
                        "topicos": list(self.Topicos_Criados),
                        "topicos_info": {
                            topico: {
                                'subscribers': len(self.Topico_Clientes[topico]),
                                'last_message': self.Topico_UltimaMensagem[topico]['timestamp']
                            } for topico in self.Topicos_Criados
                        }
                    })

                elif tipo == "cert_request":
                    print(f"[{self._get_current_timestamp()}] Cliente {endereco} solicitou certificado do broker.")
                    self._enviar_resposta(conexao, {
                        "type": "cert_response",
                        "certificado": self.certificado_pem
                    })

            except (json.JSONDecodeError, ConnectionResetError, OSError) as e:
                print(f"[{self._get_current_timestamp()}] Erro com cliente {endereco}: {str(e)}")
                break

        for topico, conexoes in self.Topico_Clientes.items():
            if conexao in conexoes:
                conexoes.remove(conexao)
                print(f"[{self._get_current_timestamp()}] {endereco} removido do tópico '{topico}'")
        conexao.close()

    def Iniciando_Broker(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind(("localhost", 6666))
        servidor.listen()
        print(f"[{self._get_current_timestamp()}] Servidor aguardando conexões na porta 6666...")

        while True:
            conexao, endereco = servidor.accept()
            threading.Thread(target=self.Tratando_Cliente, args=(conexao, endereco)).start()


if __name__ == "__main__":
    broker = Broker()
    broker.Iniciando_Broker()
