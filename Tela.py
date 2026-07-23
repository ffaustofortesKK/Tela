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

# 0. COMANDO PARAR / RESET
if comando == "parar" or (not comando and not url_video and not cantor_atual):
    if comando == "parar":
        requests.patch(URL_STATUS, json={"comando": "clipe", "cantor": "", "musica": "", "url_video": st.session_state.ultimo_clipe_valido})
    st.rerun()

# 1. CONTAGEM DECRESCENTE (3, 2, 1, 0)
elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:80px; color:white;'>
            <h1 style='font-size: 2.5rem; color: #00ff00;'>A CHAMAR AO PALCO:</h1>
            <h2 style='font-size: 3.5rem;' class="cantor-style">{str(cantor_atual).upper()}</h2>
            <h3 style='font-size: 2rem; color: yellow;'>{str(musica_atual).upper()}</h3>
            <hr style='width: 50%; margin: 20px auto; border-color: #444;'>
            <p style='font-size: 1.5rem; color: #ccc;'>O palco vai abrir em:</p>
        </div>
    """, unsafe_allow_html=True)
    
    placeholder_contagem = st.empty()
    for i in [3, 2, 1, 0]:
        placeholder_contagem.markdown(f'<div class="contador-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    requests.patch(URL_STATUS, json={"comando": "play"})
    st.rerun()

# 2. EXECUÇÃO DO KARAOKE (FECHA E SAI IMEDIATAMENTE AO TERMINAR OU PARAR)
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
        
        video.play().catch(error => {{
            video.muted = true;
            video.play();
            setTimeout(() => {{ video.muted = false; }}, 500);
        }});

        let acaoExecutada = false;

        function sairDoKaraoke() {{
            if (acaoExecutada) return;
            acaoExecutada = true;

            // 1. Para o vídeo localmente de imediato
            video.pause();
            video.currentTime = 0;

            // 2. Atualiza o Firebase e força o redirecionamento absoluto para limpar o estado
            fetch('{URL_STATUS}', {{
                method: 'PATCH',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    "comando": "clipe",
                    "cantor": "",
                    "musica": "",
                    "url_video": "{st.session_state.ultimo_clipe_valido}"
                }})
            }}).finally(() => {{
                window.location.replace(window.location.href.split('?')[0] + '?prestador={slug}&t=' + new Date().getTime());
            }});
        }}

        // Quando o vídeo termina naturalmente
        video.onended = function() {{
            sairDoKaraoke();
        }};

        // Monitorização contínua rápida (a cada 1 segundo) para detetar se o prestador clicou em "Parar Vídeo na Tela"
        setInterval(() => {{
            fetch('{URL_STATUS}?nocache=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {{
                    if (!data || data.comando === 'parar' || data.comando === 'clipe' || !data.url_video || data.url_video !== '{url_video}') {{
                        sairDoKaraoke();
                    }}
                }}).catch(err => console.log(err));
        }}, 1000);
    </script>
    """
    components.html(player_karaoke_html, height=750)

# 3. TELA PRINCIPAL: FILA DE ESPERA E MINI-PLAYER
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
            else:
                st.markdown(f"<p style='color: #00ff00; font-weight: bold; margin-bottom: 5px;'>▶️ Reproduzindo vídeo</p>", unsafe_allow_html=True)
            
            mini_player_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body, html {{
                        margin: 0; padding: 0; width: 430px; height: 306px; background: black; overflow: hidden;
                    }}
                    .mini-container {{
                        position: relative; width: 430px; height: 306px; background: black; display: flex; justify-content: center; align-items: center;
                    }}
                    video {{
                        width: 100%; height: 100%; object-fit: fill;
                    }}
                    .mini-controls {{
                        position: absolute; bottom: 5px; left: 5px; right: 5px;
                        background: rgba(0, 0, 0, 0.85); border: 1px solid #ffd700;
                        padding: 5px 10px; border-radius: 6px; display: flex; align-items: center; gap: 8px; box-sizing: border-box;
                    }}
                    .mini-controls button {{
                        background: #ffd700; border: none; color: black; font-weight: bold;
                        padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;
                    }}
                    .mini-time {{ color: white; font-family: monospace; font-size: 0.75rem; }}
                </style>
            </head>
            <body>
                <div class="mini-container">
                    <video id="mini-video" autoplay loop muted playsinline>
                        <source src="{url_clipe}" type="video/mp4">
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
                    const seek = document.getElementById('mini-seek');
                    const timeLbl = document.getElementById('mini-time');
                    const btnPlay = document.getElementById('btn-play-pause');
                    const btnAudio = document.getElementById('btn-audio');

                    v.play().catch(e => console.log(e));

                    v.ontimeupdate = function() {{
                        if (v.duration) {{
                            seek.value = (v.currentTime / v.duration) * 100;
                            let m = Math.floor(v.currentTime / 60);
                            let s = Math.floor(v.currentTime % 60);
                            timeLbl.innerText = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                        }}
                    }};

                    function togglePlay() {{
                        if (v.paused) {{ v.play(); btnPlay.innerText = "⏸️"; }}
                        else {{ v.pause(); btnPlay.innerText = "▶️"; }}
                    }}

                    function mudarSeek(val) {{
                        if (v.duration) {{ v.currentTime = (val * v.duration) / 100; }}
                    }}

                    function mudarAudio() {{
                        v.muted = !v.muted;
                        btnAudio.innerText = v.muted ? "🔇" : "🔊";
                    }}

                    setInterval(() => {{
                        fetch('{URL_STATUS}?nocache=' + new Date().getTime())
                            .then(response => response.json())
                            .then(data => {{
                                if (data && (data.comando === 'aguardando_play' || data.comando === 'play')) {{
                                    window.location.reload();
                                }}
                            }}).catch(err => console.log(err));
                    }}, 2000);
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

    time.sleep(3)
    st.rerun()
