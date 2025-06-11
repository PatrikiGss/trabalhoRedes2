import streamlit as st
import time
from subscriber import Subscriber  

# Inicializa ou recupera uma instância do Subscriber
if 'subscriber' not in st.session_state:
    st.session_state.subscriber = Subscriber()
    st.session_state.inscrito = False
    st.session_state.topico_atual = ""
    st.session_state.mensagens_recebidas = []

subscriber = st.session_state.subscriber

st.title("SUBSCRIBER")

# Seção para listar e escolher tópicos
st.header("Inscrever-se em um Tópico")

if st.button("Lista de tópicos"):
    st.session_state.topicos = subscriber.ListaTopicos()

topicos = st.session_state.get("topicos", [])

if topicos:
    topico_selecionado = st.selectbox("Escolha um tópico para se inscrever", topicos)
    if st.button("Inscrever-se"):
        if not st.session_state.inscrito:
            subscriber.iniciar_escuta(topico_selecionado)
            st.session_state.inscrito = True
            st.session_state.topico_atual = topico_selecionado
else:
    st.text("Nenhum tópico disponível. Clique no botão acima para atualizar.")

# Seção para enviar mensagens
if st.session_state.inscrito:
    st.header("Publicar Mensagem")
    mensagem = st.text_input("Digite sua mensagem")
    if st.button("Enviar mensagem"):
        subscriber.publish(st.session_state.topico_atual, mensagem)

# Exibição das mensagens recebidas
st.header("Mensagens Recebidas")
placeholder = st.empty()

# Atualiza as mensagens recebidas (exibe as últimas 10)
while True:
    if subscriber.mensagens:
        novas = subscriber.mensagens[len(st.session_state.mensagens_recebidas):]
        st.session_state.mensagens_recebidas.extend(novas)
        placeholder.text("\n".join(st.session_state.mensagens_recebidas[-10:]))
    time.sleep(1)
