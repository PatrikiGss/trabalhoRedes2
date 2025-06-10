import streamlit as st
from subscriber import Subscriber
from streamlit_autorefresh import st_autorefresh
import socket
import json

# Função auxiliar para publicação
def publicar_mensagem(topico: str, mensagem: str, host="localhost", porta=6666):
    try:
        pacote = {
            "type": "publish",
            "topico": topico,
            "mensagem": mensagem
        }

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, porta))
        s.sendall(json.dumps(pacote).encode("utf-8"))
        s.close()

        return f"Mensagem publicada no tópico: {topico}"
    except Exception as e:
        return f"Erro ao publicar mensagem: {e}"

# Evita recriar o objeto em cada execução
if 'sub' not in st.session_state:
    st.session_state.sub = Subscriber()
sub = st.session_state.sub

st.title("📥 Assinante de Tópicos (Subscriber)")

# Botão para listar os tópicos
if st.button("🔍 Listar Tópicos Disponíveis"):
    topicos = sub.ListaTopicos()
    if topicos:
        st.session_state.topicos_disponiveis = topicos
    else:
        st.warning("Nenhum tópico disponível no momento.")

# Selectbox com tópicos disponíveis
topico_escolhido = st.selectbox(
    "Selecione um tópico existente:",
    st.session_state.get('topicos_disponiveis', []),
    key="topico_select"
)

# Campo de mensagem
mensagem = st.text_area("Insira a mensagem para publicação:")

# Botão de publicação
if st.button("📤 Publicar Mensagem"):
    if not topico_escolhido or not mensagem.strip():
        st.warning("⚠️ Por favor, preencha o tópico e a mensagem.")
    else:
        resultado = publicar_mensagem(topico_escolhido, mensagem)
        st.success(resultado)

# Botão de inscrição
if st.button("✅ Inscrever-se"):
    if topico_escolhido:
        sub.subscribe(topico_escolhido)
        st.success(f"Inscrito no tópico: {topico_escolhido}")
    else:
        st.error("Informe um tópico válido.")

# Auto-refresh a cada 1 segundo
st_autorefresh(interval=1000, key="auto_refresh")

# Mensagens recebidas
st.subheader("📨 Mensagens Recebidas:")
if hasattr(sub, 'mensagens') and sub.mensagens:
    for msg in sub.mensagens[::-1]:
        st.write(msg)
else:
    st.info("Nenhuma mensagem recebida ainda.")
