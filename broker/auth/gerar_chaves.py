from broker.auth.chaves import GerenciadorChaves

chaves = GerenciadorChaves()
chaves.gerar_chave_privada()
chaves.gerar_chave_publica()
print("🔐 Chaves RSA geradas com sucesso.")
