import streamlit as st
from publisher import publicar_topico   
st.title("PUBLISHER")
st.write("Envie mensagens para um tópico específico")
topico = st.text_input("Insira o tópico:")

# Botão para publicar
if st.button("🚀 Publicar topico"):
    if topico.strip() == "":
        st.warning("⚠️ Por favor, preencha o tópico e a mensagem antes de enviar.")
    else:
        resultado = publicar_topico(topico)
        st.success(resultado)