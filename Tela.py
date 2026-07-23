import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# Obter o prestador pela URL (ex: ?prestador=geral)
params = st.query_params
slug = params.get("prestador", "geral")

# URL do Firebase para os pedidos deste prestador
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

# Buscar os dados da fila no Firebase
try:
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_pedidos = {}

# Título da Tela
st.markdown("<h1 style='color: gold; font-size: 2.2rem; margin-bottom: 15px;'>🎤 FILA DE ESPERA</h1>", unsafe_allow_html=True)

# Exibir a lista de cantores
if res_pedidos:
    pedidos_lista = list(res_pedidos.items())
    contador_exibicao = 1
    
    for p_id, p in pedidos_lista:
        if not str(p.get('musica', '')).startswith("PEDIDO:"):
            cantor = str(p.get('cantor', 'Desconhecido')).upper()
            musica = str(p.get('musica', 'Música Desconhecida')).upper()
            
            st.markdown(
                f"<h3 style='margin: 10px 0; font-size: 1.5rem;'>"
                f"{contador_exibicao}. <span style='color: white;'>{cantor}</span> ➔ <span style='color: yellow;'>{musica}</span>"
                f"</h3>", 
                unsafe_allow_html=True
            )
            contador_exibicao += 1
            
    if contador_exibicao == 1:
        st.info("Ainda sem cantores na fila.")
else:
    st.info("A fila está vazia. Envie músicas pelo telemóvel!")

# Atualiza automaticamente a cada 3 segundos para apanhar novos pedidos
time.sleep(3)
st.rerun()
