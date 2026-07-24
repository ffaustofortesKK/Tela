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
id_sessao = res_status.get("id_sessao", "default")

if comando in ["parar", None, ""]:
    if url_video or cantor_atual or musica_atual:
        try:
            requests.put(URL_STATUS, json={"comando": "parar", "cantor": "", "musica": "", "url_video": "", "id_sessao": "limpo"})
        except:
            pass
        url_video = ""

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
            const sessaoAtual = "{id_sessao}";
            
            if (sessionStorage.getItem('executado_' + sessaoAtual)) {{
                window.location.replace(window.location.href.split('?')[0] + '?prestador=' + slugPrestador + '&t=' + new Date().getTime());
            }}

            const ecraIntro = document.getElementById('ecra-intro');
            const ecraVideo = document.getElementById('ecra-video');
            const divContador = document.getElementById('contador');
            const video = document.getElementById('karaokeVideo');
            const btnManual = document.getElementById('btn-manual-play');

            video.loop = false;
            let jaSaiu = false;

            function voltarParaPrincipal() {{
                if (jaSaiu) return;
                jaSaiu = true;
                
                sessionStorage.setItem('executado_' + sessaoAtual, 'true');

                video.pause();
                video.currentTime = 0;
                document.getElementById('app').innerHTML = "<h1 style='color:white; text-align:center;'>A encerrar actuação...</h1>";

                fetch(urlStatus, {{
                    method: 'PUT',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        "comando": "parar",
                        "cantor": "",
                        "musica": "",
                        "url_video": "",
                        "id_sessao": "fim_" + new Date().getTime()
                    }})
                }}).finally(() => {{
                    window.location.replace(window.location.href.split('?')[0] + '?prestador=' + slugPrestador + '&t=' + new Date().getTime());
                }});
            }}

            let count = 3;
            let timer = setInterval(() => {{
                count--;
                if (count > 0) {{
                    divContador.innerText = count;
                }} else if (count === 0) {{
                    divContador.innerText = "0";
                }} else {{
                    clearInterval(timer);
                    ecraIntro.style.display = 'none';
                    ecraVideo.style.display = 'flex';
                    video.style.display = 'block';
                    video.muted = false;
                    video.play().catch(e => {{ btnManual.style.display = 'block'; }});
                }}
            }}, 1000);

            video.onended = function() {{
                voltarParaPrincipal();
            }};

            function forcarPlay() {{
                btnManual.style.display = 'none';
                video.muted = false;
                video.play();
            }}
        </script>
    </body>
    </html>
    """
    components.html(player_seguro_html, height=750, scrolling=False)

# ESTADO NORMAL / VÍDEO CLIPE DE FUNDO
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
            
            mini_player_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body, html {{ margin: 0; padding: 0; width: 430px; height: 306px; background: black; overflow: hidden; }}
                    .mini-container {{ position: relative; width: 430px; height: 306px; background: black; display: flex; justify-content: center; align-items: center; }}
                    video {{ width: 100%; height: 100%; object-fit: fill; }}
                    .mini-controls {{ position: absolute; bottom: 5px; left: 5px; right: 5px; background: rgba(0, 0, 0, 0.85); border: 1px solid #ffd700; padding: 5px 10px; border-radius: 6px; display: flex; align-items: center; gap: 8px; box-sizing: border-box; }}
                    .mini-controls button {{ background: #ffd700; border: none; color: black; font-weight: bold; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }}
                    .mini-time {{ color: white; font-family: monospace; font-size: 0.75rem; }}
                </style>
            </head>
            <body>
                <div class="mini-container" id="mini-app">
                    <video id="mini-video" muted playsinline>
                        <source src="{url_video}" type="video/mp4">
                    </video>
                    <div class="mini-controls">
                        <button id="btn-play-pause" onclick="togglePlay()">⏸️</button>
                        <span id="mini-time" class="mini-time">00:00</span>
                        <input type="range" id="mini-seek" value="0" min="0" max="100" step="0.1" style="flex-grow: 1;" oninput="mudarSeek(this.value)">
                        <button onclick="mudarAudio()" id="btn-audio" style="background: #333; color: white;">🔇</button>
                    </div>
                </div>
                
                <script>
                    const v = document.getElementById('mini-video');
                    const sessaoAtual = "{id_sessao}";
                    
                    if (sessionStorage.getItem('executado_clipe_' + sessaoAtual)) {{
                        fetch('{URL_STATUS}', {{
                            method: 'PUT',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{"comando": "parar", "cantor": "", "musica": "", "url_video": "", "id_sessao": "fim_clipe"}})
                        }}).finally(() => {{
                            window.location.replace(window.location.href.split('?')[0] + '?prestador=' + '{slug}' + '&t=' + new Date().getTime());
                        }});
                    }}

                    v.loop = false;
                    v.autoplay = true;
                    v.play().catch(e => console.log(e));

                    v.ontimeupdate = function() {{
                        if (v.duration) {{
                            document.getElementById('mini-seek').value = (v.currentTime / v.duration) * 100;
                            let m = Math.floor(v.currentTime / 60);
                            let s = Math.floor(v.currentTime % 60);
                            document.getElementById('mini-time').innerText = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                        }}
                    }};

                    v.onended = function() {{
                        sessionStorage.setItem('executado_clipe_' + sessaoAtual, 'true');
                        v.pause();
                        document.getElementById('mini-app').innerHTML = "<div style='color: #888; text-align: center; width: 100%;'>Clipe finalizado.</div>";

                        fetch('{URL_STATUS}', {{
                            method: 'PUT',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{"comando": "parar", "cantor": "", "musica": "", "url_video": "", "id_sessao": "fim_clipe"}})
                        }}).finally(() => {{
                            window.location.replace(window.location.href.split('?')[0] + '?prestador=' + '{slug}' + '&t=' + new Date().getTime());
                        }});
                    }};

                    function togglePlay() {{
                        if (v.paused) {{ v.play(); document.getElementById('btn-play-pause').innerText = "⏸️"; }}
                        else {{ v.pause(); document.getElementById('btn-play-pause').innerText = "▶️"; }}
                    }}
                    function mudarSeek(val) {{
                        if (v.duration) {{ v.currentTime = (val * v.duration) / 100; }}
                    }}
                    function mudarAudio() {{
                        v.muted = !v.muted;
                        document.getElementById('btn-audio').innerText = v.muted ? "🔇" : "🔊";
                    }}

                    setInterval(() => {{
                        fetch('{URL_STATUS}?nocache=' + new Date().getTime())
                            .then(res => res.json())
                            .then(data => {{
                                if (data && data.url_video && data.id_sessao !== sessaoAtual) {{
                                    window.location.reload();
                                }}
                            }});
                    }}, 3000);
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
            
            espera_ativa_html = f"""
            <script>
                setInterval(() => {{
                    fetch('{URL_STATUS}?nocache=' + new Date().getTime())
                        .then(res => res.json())
                        .then(data => {{
                            if (data && data.url_video && data.comando && data.comando !== 'parar') {{
                                window.location.reload();
                            }}
                        }});
                }}, 2500);
            </script>
            """
            components.html(espera_ativa_html, height=0, scrolling=False)
