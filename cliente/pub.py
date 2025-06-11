import streamlit as st
from publisher import criar_topico


st.title("PUBLISHER")

# Campo para o tópico
topico = st.text_input("🧩 Nome do novo tópico")


# Botão para criar o tópico
if st.button("📌 Criar Tópico"):
    if not topico.strip():
        st.warning("⚠️ Por favor, preencha o nome do tópico.")
    else:
        resultado = criar_topico(topico)
        st.success(f"✅ {resultado}")
