import streamlit as st
from publisher import publicar_mensagem   
st.title(" Publicador")
st.write("Envie mensagens para um tópico específico")
topico = st.text_input("Insira o tópico:")
mensagem = st.text_area("Insira a mensagem:")
# Botão para publicar
if st.button("🚀 Publicar Mensagem"):
    if topico.strip() == "" or mensagem.strip() == "":
        st.warning("⚠️ Por favor, preencha o tópico e a mensagem antes de enviar.")
    else:
        resultado = publicar_mensagem(topico, mensagem)
        st.success(resultado)
