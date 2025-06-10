import streamlit as st
from subscriber import Subscriber
from streamlit_autorefresh import st_autorefresh

# Evita recriar o objeto em cada execução
if 'sub' not in st.session_state:
    st.session_state.sub = Subscriber()
sub = st.session_state.sub

st.title("📥 Assinante de Tópicos (Subscriber)")
if st.button("🔍 Listar Tópicos Disponíveis"):
    topicos = sub.ListaTopicos()
    if topicos:
        st.session_state.topicos_disponiveis = topicos
    else:
        st.warning("Nenhum tópico disponível no momento.")

# Lista suspensa com tópicos ou campo manual
topico_escolhido = st.selectbox("Selecione um tópico existente:", 
                                st.session_state.get('topicos_disponiveis', []))

if st.button("✅ Inscrever-se"):
    topico_final = topico_escolhido
    if topico_final:
        sub.subscribe(topico_final)
        st.success(f"Inscrito no tópico: {topico_final}")
    else:
        st.error("Informe um tópico válido.")

# Auto-refresh a cada 1 segundos
st_autorefresh(interval=1000, key="auto_refresh")
# Mostrar mensagens recebidas
st.subheader("📨 Mensagens Recebidas:")
if hasattr(sub, 'mensagens') and sub.mensagens:
    for msg in sub.mensagens[::-1]:
        st.write(msg)
else:
    st.info("Nenhuma mensagem recebida ainda.")