import streamlit as st
import requests
import time
import streamlit.components.v1 as components

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
        .contador-box { font-size: 8rem; color: yellow; font-weight: bold; text-shadow: 0 0 20px red; text-align: center; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

if "ultimo_clipe_valido" not in st.session_state:
    st.session_state.ultimo_clipe_valido = ""

# Buscar dados do Firebase
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

if comando == "clipe" and url_video:
    st.session_state.ultimo_clipe_valido = url_video

# 0. TRATAMENTO DO COMANDO PARAR
if comando == "parar":
    st.markdown("""
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: black; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 99999;">
            <h1 style="color: #ff4444; font-size: 3rem; font-family: sans-serif; text-shadow: 2px 2px 8px #000;">⏹️ ATUAÇÃO PARADA</h1>
            <p style="color: #ccc; font-size: 1.5rem; font-family: sans-serif;">Aguardando o próximo comando do prestador...</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.rerun()

# 1. CONTAGEM DECRESCENTE (3, 2, 1, 0) E SALTO AUTOMÁTICO PARA PLAY
elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:60px; color:white;'>
            <h1 style='font-size: 2.2rem; color: #00ff00;'>A CHAMAR AO PALCO:</h1>
            <h2 style='font-size: 3rem;' class="cantor-style">{str(cantor_atual).upper()}</h2>
            <h3 style='font-size: 1.8rem; color: yellow;'>{str(musica_atual).upper()}</h3>
            <hr style='width: 40%; margin: 15px auto; border-color: #444;'>
            <p style='font-size: 1.3rem; color: #ccc;'>O palco vai abrir em:</p>
        </div>
    """, unsafe_allow_html=True)
    
    placeholder_contagem = st.empty()
    for i in [3, 2, 1, 0]:
        placeholder_contagem.markdown(f'<div class="contador-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    # Atualiza automaticamente no Firebase para o estado 'play' para o vídeo arrancar sozinho
    requests.patch(URL_STATUS, json={"comando": "play"})
    st.rerun()

# 2. EXECUÇÃO DO VÍDEO DE KARAOKE (ARRANCA SOZINHO E FECHA LOGO AO TERMINAR)
elif comando == "play":
    player_karaoke_html = f"""
    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: black; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 99999;">
        <div style="position: absolute; top: 15px; text-align: center; width: 100%;">
            <h2 style="color: #00ffcc; font-family: sans-serif; margin: 0; text-shadow: 2px 2px 4px #000;">🎤 A cantar: {str(cantor_atual).upper()} - {str(musica_atual).upper()}</h2>
        </div>
        <video id="karaokeVideo" width="100%" height="90%" autoplay controls style="object-fit: contain;">
            <source src="{url_video}" type="video/mp4">
            O seu browser não suporta vídeo.
        </video>
    </div>
    <script>
        var video = document.getElementById('karaokeVideo');
        video.muted = false;
        video.loop = false;
        
        // Força o início automático imediato
        video.play().catch(error => {{
            console.log("Autoplay bloqueado, a tentar com mudo:", error);
            video.muted = true;
            video.play();
            setTimeout(() => {{ video.muted = false; }}, 400);
        }});

        let jaSaiu = false;

        function sairDoKaraoke() {{
            if (jaSaiu) return;
            jaSaiu = true;

            // Restaura o clipe de fundo anterior e sai do modo karaoke
            fetch('{URL_STATUS}', {{
                method: 'PATCH',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    "comando": "clipe",
                    "url_video": "{st.session_state.ultimo_clipe_valido}",
                    "cantor": "",
                    "musica": ""
                }})
            }}).then(() => {{
                window.location.href = window.location.href.split('?')[0] + '?prestador={slug}&nocache=' + new Date().getTime();
            }}).catch(() => {{
                window.location.reload();
            }});
        }}

        // Assim que o vídeo de karaoke termina, fecha e regressa à tela inicial
        video.onended = sairDoKaraoke;

        video.ontimeupdate = function() {{
            if (video.duration && (video.duration - video.currentTime < 0.4)) {{
                sairDoKaraoke();
            }}
        }};
    </script>
    """
    components.html(player_karaoke_html, height=750)

# 3. TELA PRINCIPAL: FILA DE ESPERA À ESQUERDA E VÍDEO CLIPE À DIREITA
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
        
        url_clipe = res_status.get("url_video")
        nome_clipe_atual = res_status.get("musica")

        if url_clipe:
            if nome_clipe_atual:
                st.markdown(f"<p style='color: #00ff00; font-weight: bold; margin-bottom: 5px;'>▶️ Reproduzindo: {nome_clipe_atual}</p>", unsafe_allow_html=True)
            
            mini_player_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body, html {{ margin: 0; padding: 0; width: 430px; height: 306px; background: black; overflow: hidden; }}
                    .mini-container {{ position: relative; width: 430px; height: 306px; background: black; display: flex; justify-content: center; align-items: center; }}
                    video {{ width: 100%; height: 100%; object-fit: fill; }}
                </style>
            </head>
            <body>
                <div class="mini-container">
                    <video id="mini-video" autoplay loop muted playsinline>
                        <source src="{url_clipe}" type="video/mp4">
                    </video>
                </div>
                <script>
                    const v = document.getElementById('mini-video');
                    v.play().catch(e => console.log(e));
                </script>
            </body>
            </html>
            """
            components.html(mini_player_html, height=316, scrolling=False)
        else:
            st.markdown("""
                <div class="video-clipe-box" style="display: flex; align-items: center; justify-content: center; text-align: center; color: #888; padding: 20px;">
                    <p style="margin: 0; font-size: 1rem;">Aguardando o prestador selecionar um vídeo clipe no painel de controle...</p>
                </div>
            """, unsafe_allow_html=True)

    # Atualiza a cada 2 segundos para apanhar instantaneamente qualquer clique do prestador (mudar de cantor, parar, etc.)
    time.sleep(2)
    st.rerun()
