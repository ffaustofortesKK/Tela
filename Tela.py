import streamlit as st
import time

st.set_page_config(page_title="TESTE DE VÍDEO NATIVO", layout="wide")

st.markdown("<h1 style='color: white;'>🧪 Teste de Vídeo Nativo (Sem Componentes HTML)</h1>", unsafe_allow_html=True)

# Link de vídeo público de teste em MP4
url_teste = "https://www.w3schools.com/html/mov_bbb.mp4"

st.write(f"A testar reprodução nativa com o link: `{url_teste}`")

# Utilização do player nativo do Streamlit (ignora bloqueios de iframe/HTML)
st.video(url_teste, format="video/mp4", autoplay=True, muted=True)
