import streamlit as st
import requests
import time
import cloudinary
import cloudinary.search
import streamlit.components.v1 as components

# Configuração Cloudinary
cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: black; margin: 0; padding: 0; overflow: hidden; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .contador-box { font-size: 8rem; color: yellow; font-weight: bold; text-shadow: 0 0 20px red; text-align: center; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

# Buscar dados do Firebase
try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}
    res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

# 1. CONTAGEM DECRESCENTE (3, 2, 1, 0) ANTES DE EXECUTAR O PEDIDO
if comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:80px; color:white;'>
            <h1 style='font-size: 2.5rem; color: #00ff00;'>A CHAMAR AO PALCO:</h1>
            <h2 style='font-size: 3.5rem;' class="cantor-style">{str(res_status.get('cantor', '')).upper()}</h2>
            <h3 style='font-size: 2rem; color: yellow;'>{str(res_status.get('musica', '')).upper()}</h3>
            <hr style='width: 50%; margin: 20px auto; border-color: #444;'>
            <p style='font-size: 1.5rem; color: #ccc;'>O palco vai abrir em:</p>
        </div>
    """, unsafe_allow_html=True)
    
    placeholder_contagem = st.empty()
    for i in [3, 2, 1, 0]:
        placeholder_contagem.markdown(f'<div class="contador-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    requests.patch(URL_STATUS, json={"comando": "fim"})
    st.rerun()

# 2. TELA PRINCIPAL: FILA DE ESPERA À ESQUERDA E PLAYER À DIREITA
else:
    st.markdown("<h1 style='color:white; font-size: 2.2rem; margin-bottom: 20px;'>📺 FFKaraoke — Palco Principal</h1>", unsafe_allow_html=True)
    
    cl1, cl2 = st.columns([1.4, 1.2])

    with cl1:
        st.markdown("<h3 style='color:gold; font-size: 1.8rem; margin-bottom: 15px;'>🎤 FILA DE ESPERA</h3>", unsafe_allow_html=True)
        
        if res_pedidos:
            pedidos_lista = list(res_pedidos.items())
            contador_exibicao = 1
            for p_id, p in pedidos_lista:
                if not str(p.get('musica', '')).startswith("PEDIDO:"):
                    st.markdown(f"<h4 style='margin: 10px 0; font-size: 1.2rem;'>{contador_exibicao}. <span class='cantor-style'>{str(p.get('cantor')).upper()}</span> ➔ <span class='musica-style'>{str(p.get('musica')).upper()}</span></h4>", unsafe_allow_html=True)
                    contador_exibicao += 1
            if contador_exibicao == 1:
                st.info("Ainda sem cantores na fila.")
        else:
            st.info("A fila está vazia. Envie músicas pelo telemóvel!")

    with cl2:
        st.markdown("<h3 style='color:gold; font-size: 1.8rem; margin-bottom: 5px;'>📺 VÍDEO CLIPE (FUNDO)</h3>", unsafe_allow_html=True)
        
        nome_clipe_atual = res_status.get("musica")

        if url_video:
            if nome_clipe_atual:
                st.markdown(f"<p style='color: #00ff00; font-weight: bold; margin-bottom: 5px;'>▶️ Reproduzindo: {nome_clipe_atual}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color: #00ff00; font-weight: bold; margin-bottom: 5px;'>▶️ Reproduzindo vídeo</p>", unsafe_allow_html=True)
            
            player_iframe_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body, html {{
                        margin: 0; padding: 0; width: 430px; height: 306px; background: black; overflow: hidden;
                    }}
                    iframe {{
                        width: 430px; height: 306px; border: none; background: black;
                    }}
                </style>
            </head>
            <body>
                <video id="video-player" width="430" height="306" controls autoplay style="background: black; object-fit: fill;">
                    <source src="{url_video}" type="video/mp4">
                    <source src="{url_video}" type="video/webm">
                    Seu navegador não suporta a tag de vídeo.
                </video>
                <script>
                    const vid = document.getElementById('video-player');
                    vid.play().catch(error => {{
                        vid.muted = true;
                        vid.play();
                    }});
                </script>
            </body>
            </html>
            """
            components.html(player_iframe_html, height=316, scrolling=False)
        else:
            st.markdown("""
                <div style="width: 430px; height: 306px; background: black; border: 2px solid #ffd700; border-radius: 4px; display: flex; align-items: center; justify-content: center; text-align: center; color: #888; padding: 20px;">
                    <p style="margin: 0; font-size: 1rem;">Aguardando o prestador selecionar um vídeo clipe no painel de controle...</p>
                </div>
            """, unsafe_allow_html=True)

    time.sleep(3)
    st.rerun()
