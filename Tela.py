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

# SE O COMANDO FOR PARA CANTAR (KARAOKE)
if comando in ["aguardando_play", "play"] and url_video:
    
    player_seguro_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body, html {{
                margin: 0; padding: 0; width: 100vw; height: 100vh; background: black; overflow: hidden; font-family: sans-serif;
            }}
            .fullscreen-container {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: black;
                display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 99999;
            }}
            .header-info {{
                position: absolute; top: 15px; text-align: center; width: 100%; z-index: 100000;
            }}
            .header-info h2 {{
                color: #00ffcc; margin: 0; text-shadow: 2px 2px 4px #000; font-size: 1.8rem;
            }}
            .contador-box {{
                font-size: 10rem; color: yellow; font-weight: bold; text-shadow: 0 0 30px red; text-align: center;
            }}
            .intro-text {{
                text-align: center; color: white; padding: 20px;
            }}
            .intro-text h1 {{ color: #00ff00; font-size: 2.2rem; margin-bottom: 10px; }}
            .intro-text h2 {{ font-size: 3rem; color: white; text-shadow: 2px 2px 4px #000; margin: 5px 0; }}
            .intro-text h3 {{ font-size: 1.8rem; color: yellow; text-shadow: 2px 2px 4px #000; margin: 5px 0; }}
            
            #btn-manual-play {{
                display: none; position: absolute; z-index: 100001;
                background: #00ff00; color: black; font-size: 2rem; font-weight: bold;
                padding: 20px 40px; border: none; border-radius: 12px; cursor: pointer;
                box-shadow: 0 0 30px #00ff00;
            }}
            video {{
                width: 100%; height: 90%; object-fit: contain; display: none;
            }}
        </style>
    </head>
    <body>
        <div id="app" class="fullscreen-container">
            <div id="ecra-intro" class="intro-text">
                <h1>A CHAMAR AO PALCO:</h1>
                <h2 id="txt-cantor">{str(cantor_atual).upper()}</h2>
                <h3 id="txt-musica">{str(musica_atual).upper()}</h3>
                <hr style="width: 50%; margin: 20px auto; border-color: #444;">
                <p style="font-size: 1.5rem; color: #ccc;">O palco vai abrir em:</p>
                <div id="contador" class="contador-box">3</div>
            </div>

            <button id="btn-manual-play" onclick="forcarPlay()">▶ CLIQUE AQUI PARA INICIAR VÍDEO</button>

            <div id="ecra-video" style="display:none; width:100%; height:100%; justify-content:center; align-items:center;">
                <div class="header-info">
                    <h2>🎤 A cantar: {str(cantor_atual).upper()} - {str(musica_atual).upper()}</h2>
                </div>
                <video id="karaokeVideo" controls playsinline>
                    <source src="{url_video}" type="video/mp4">
                    O seu browser não suporta vídeo.
                </video>
            </div>
        </div>

        <script>
            const urlStatus = "{URL_STATUS}";
            const slugPrestador = "{slug}";
            const urlVideoAtual = "{url_video}";
            const cantorAtual = "{str(cantor_atual)}";

            const ecraIntro = document.getElementById('ecra-intro');
            const ecraVideo = document.getElementById('ecra-video');
            const divContador = document.getElementById('contador');
            const video = document.getElementById('karaokeVideo');
            const btnManual = document.getElementById('btn-manual-play');

            let loopVerificacao = null;
            let jaSaiu = false;
            video.loop = false;

            function voltarParaPrincipal() {{
                if (jaSaiu) return;
                jaSaiu = true;
                if (loopVerificacao) clearInterval(loopVerificacao);

                video.pause();
                video.removeAttribute('src');
                video.load();

                fetch(urlStatus, {{
                    method: 'PATCH',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        "comando": "parar",
                        "cantor": "",
                        "musica": "",
                        "url_video": ""
                    }})
                }}).finally(() => {{
                    window.location.replace(window.location.href.split('?')[0] + '?prestador=' + slugPrestador + '&t=' + new Date().getTime());
                }});
            }}

            let count = 3;
            function iniciarContagem() {{
                let timer = setInterval(() => {{
                    count--;
                    if (count > 0) {{
                        divContador.innerText = count;
                    }} else if (count === 0) {{
                        divContador.innerText = "0";
                    }} else {{
                        clearInterval(timer);
                        transitarParaVideo();
                    }}
                }}, 1000);
            }}

            function transitarParaVideo() {{
                ecraIntro.style.display = 'none';
                ecraVideo.style.display = 'flex';
                video.style.display = 'block';

                video.muted = false;
                let p = video.play();
                if (p !== undefined) {{
                    p.catch(error => {{
                        console.log("Autoplay bloqueado pelo browser.");
                        btnManual.style.display = 'block';
                    }});
                }}

                video.onended = function() {{
                    voltarParaPrincipal();
                }};

                loopVerificacao = setInterval(() => {{
                    fetch(urlStatus + '?nocache=' + new Date().getTime())
                        .then(res => res.json())
                        .then(data => {{
                            if (!data || data.comando === 'parar' || data.comando === 'clipe' || !data.url_video || data.url_video !== urlVideoAtual || data.cantor !== cantorAtual) {{
                                window.location.replace(window.location.href.split('?')[0] + '?prestador=' + slugPrestador + '&t=' + new Date().getTime());
                            }}
                        }}).catch(err => console.log(err));
                }}, 800);
            }}

            function forcarPlay() {{
                btnManual.style.display = 'none';
                video.muted = false;
                video.play();
            }}

            setTimeout(iniciarContagem, 500);
        </script>
    </body>
    </html>
    """
    components.html(player_seguro_html, height=750, scrolling=False)

# ESTADO NORMAL / PARAR (Fila de espera e vídeo de fundo)
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
        
        # EXTREMA RIGIDEZ: O vídeo clipe SÓ toca se o comando for explicitamente "clipe" 
        # E se houver um timestamp recente ou ordem ativa. Caso contrário, limpa imediatamente o Firebase!
        if comando == "clipe" and url_video:
            # Vamos limpar automaticamente no Firebase para que ele nunca mais volte a reaparecer sozinho num futuro F5
            try:
                requests.patch(URL_STATUS, json={"comando": "parar", "url_video": "", "musica": ""})
            except:
                pass
            
            st.markdown("""
                <div class="video-clipe-box" style="display: flex; align-items: center; justify-content: center; text-align: center; color: #888; padding: 20px;">
                    <p style="margin: 0; font-size: 1rem;">Aguardando o prestador selecionar um vídeo clipe no painel de controle...</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="video-clipe-box" style="display: flex; align-items: center; justify-content: center; text-align: center; color: #888; padding: 20px;">
                    <p style="margin: 0; font-size: 1rem;">Aguardando o prestador selecionar um vídeo clipe no painel de controle...</p>
                </div>
            """, unsafe_allow_html=True)

    time.sleep(3)
    st.rerun()
