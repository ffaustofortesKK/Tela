import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: black; margin: 0; padding: 0; overflow: hidden; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .video-clipe-box { 
            width: 430px; 
            height: 306px;
            background: black; 
            padding: 0px; 
            border-radius: 4px; 
            border: 2px solid #ffd700; 
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}
    res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")
cantor_atual = res_status.get("cantor")
musica_atual = res_status.get("musica")
acao_player = res_status.get("acao_player")

# Se o comando for parar ou stop, limpa tudo no Firebase e força o refresh imediato
if comando in ["parar", None, ""] or acao_player == "stop":
    if url_video or cantor_atual or musica_atual or acao_player == "stop":
        try:
            requests.put(URL_STATUS, json={"comando": "parar", "cantor": "", "musica": "", "url_video": "", "acao_player": "", "id_sessao": "limpo"})
        except:
            pass
    # Recarrega a página para limpar qualquer vestígio de vídeo
    st.rerun()

# 1. MODO KARAOKE (Ecrã Inteiro)
if comando in ["aguardando_play", "play"] and url_video:
    st.markdown(f"<h1 style='color: #00ffcc; text-align: center; margin-top: 20px;'>🎤 A CANTAR: {str(cantor_atual).upper()} - {str(musica_atual).upper()}</h1>", unsafe_allow_html=True)
    
    st.video(url_video, format="video/mp4", autoplay=True)
    
    # Deteta se o prestador clicou em stop/parar no painel
    time.sleep(3)
    st.rerun()

# 2. ESTADO NORMAL: FILA + VÍDEO CLIPE DE FUNDO (Nativo)
else:
    cl1, cl2 = st.columns([1.4, 1.2])

    with cl1:
        st.markdown("<h1 style='color:gold; font-size: 2.2rem; margin-bottom: 15px;'>🎤 FILA DE ESPERA</h1>", unsafe_allow_html=True)
        if res_pedidos:
            pedidos_lista = list(res_pedidos.items())
            contador_exibicao = 1
            for p_id, p in pedidos_lista:
                if not str(p.get('musica', '')).startswith("PEDIDO:"):
                    st.markdown(f"<h3 style='margin: 10px 0; font-size: 1.3rem;'>{contador_exibicao}. <span class='cantor-style'>{str(p.get('cantor')).upper()}</span> ➔ <span class='musica-style'>{str(p.get('musica')).upper()}</span></h3>", unsafe_allow_html=True)
                    contador_exibicao += 1
            if contador_exibicao == 1:
                st.info("Ainda sem cantores na fila.")
        else:
            st.info("A fila está vazia. Envie músicas pelo telemóvel!")

    with cl2:
        st.markdown("<h1 style='color:gold; font-size: 1.8rem; margin-bottom: 5px;'>📺 VÍDEO CLIPE (FUNDO)</h1>", unsafe_allow_html=True)
        
        if comando == "clipe" and url_video:
            nome_clipe_atual = res_status.get("musica")
            st.markdown(f"<p style='color: #00ff00; font-weight: bold; margin-bottom: 5px;'>▶️ Reproduzindo: {nome_clipe_atual or 'Vídeo'}</p>", unsafe_allow_html=True)
            
            # Reprodutor nativo limpo do Streamlit para o clipe de fundo
            st.video(url_video, format="video/mp4", autoplay=True, muted=True, loop=True)
            
            # Pequena pausa e verificação contínua do estado no Firebase para atualizar se houver Stop
            time.sleep(3)
            st.rerun()
        else:
            st.markdown("""
                <div class="video-clipe-box" style="display: flex; align-items: center; justify-content: center; text-align: center; color: #888; padding: 20px;">
                    <p style="margin: 0; font-size: 1rem;">Aguardando o prestador selecionar um vídeo clipe no painel de controle...</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Fica à escuta por novos comandos na nuvem
            time.sleep(3)
            st.rerun()
