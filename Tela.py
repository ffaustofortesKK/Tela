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
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=3).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=3).json() or {}
except:
    res_status = {}
    res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")
cantor_atual = res_status.get("cantor")
musica_atual = res_status.get("musica")
id_sessao = res_status.get("id_sessao", "default")

# SE FOR PARA EXECUTAR O KARAOKE EM TELA INTEIRA
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
                <h2>{str(cantor_atual).upper()}</h2>
                <h3>{str(musica_atual).upper()}</h3>
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
                </video>
            </div>
        </div>

        <script>
            const urlStatus = "{URL_STATUS}";
            const slugPrestador = "{slug}";
            const video = document.getElementById('karaokeVideo');
            const btnManual = document.getElementById('btn-manual-play');
            const ecraIntro = document.getElementById('ecra-intro');
            const ecraVideo = document.getElementById('ecra-video');
            const divContador = document.getElementById('contador');

            video.loop = false;
            let jaSaiu = false;

            function voltarParaPrincipal() {{
                if (jaSaiu) return;
                jaSaiu = true;
                video.pause();

                fetch(urlStatus, {{
                    method: 'PUT',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{"comando": "parar", "cantor": "", "musica": "", "url_video": "", "id_sessao": "fim_" + Date.now()}})
                }}).finally(() => {{
                    window.location.replace(window.location.href.split('?')[0] + '?prestador=' + slugPrestador + '&t=' + Date.now());
                }});
            }}

            let count = 3;
            let timer = setInterval(() => {{
                count--;
                if (count > 0) {{
                    divContador.innerText = count;
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

# ESTADO NORMAL (FILA + GESTÃO INTELIGENTE DE VÍDEO CLIPE EM JS AUTÓNOMO)
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
        
        # BLOCO ÚNICO AUTÓNOMO EM JAVASCRIPT: Lê o Firebase diretamente sem re-renderizações infinitas do Streamlit
        painel_autonomo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body, html {{ margin: 0; padding: 0; width: 430px; height: 310px; background: black; overflow: hidden; font-family: sans-serif; }}
                .box-clipe {{ position: relative; width: 430px; height: 306px; background: black; border: 2px solid #ffd700; border-radius: 6px; display: flex; justify-content: center; align-items: center; overflow: hidden; }}
                video {{ width: 100%; height: 100%; object-fit: fill; }}
                .aviso-espera {{ color: #888; text-align: center; padding: 20px; font-size: 1rem; }}
                .controlo-barra {{ position: absolute; bottom: 5px; left: 5px; right: 5px; background: rgba(0, 0, 0, 0.85); border: 1px solid #ffd700; padding: 5px 10px; border-radius: 6px; display: none; align-items: center; gap: 8px; box-sizing: border-box; }}
                .controlo-barra button {{ background: #ffd700; border: none; color: black; font-weight: bold; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }}
                .tempo-txt {{ color: white; font-family: monospace; font-size: 0.75rem; }}
                #titulo-reproducao {{ color: #00ff00; font-weight: bold; font-size: 0.9rem; margin-bottom: 5px; height: 20px; }}
            </style>
        </head>
        <body>
            <div id="titulo-reproducao">Aguardando seleção...</div>
            <div class="box-clipe" id="containerClipe">
                <div id="msg-status" class="aviso-espera">Aguardando o prestador selecionar um vídeo clipe no painel de controle...</div>
                <video id="videoClipe" playsinline style="display:none;"></video>
                <div class="controlo-barra" id="barraControlo">
                    <button id="btnPlayPause" onclick="controlarPlay()">⏸️</button>
                    <span id="txtTempo" class="tempo-txt">00:00</span>
                    <input type="range" id="barraSeek" value="0" min="0" max="100" step="0.1" style="flex-grow: 1;" oninput="ajustarSeek(this.value)">
                    <button onclick="ajustarAudio()" id="btnAudio" style="background: #333; color: white;">🔇</button>
                </div>
            </div>

            <script>
                const urlStatus = "{URL_STATUS}";
                const slugTV = "{slug}";
                const vid = document.getElementById('videoClipe');
                const msgStatus = document.getElementById('msg-status');
                const barraControlo = document.getElementById('barraControlo');
                const tituloRep = document.getElementById('titulo-reproducao');
                
                let ultimoTokenProcessado = "";

                vid.loop = false;
                vid.muted = true;

                function verificarEstadoFirebase() {{
                    fetch(urlStatus + '?nocache=' + Date.now())
                        .then(res => res.json())
                        .then(data => {{
                            if (!data) return;

                            // Se houver comando para cantar, força reload para abrir o ecrã completo de karaoke
                            if (data.comando === 'aguardando_play' || data.comando === 'play') {{
                                window.location.reload();
                                return;
                            }}

                            // Se o comando for clipe e houver URL novo
                            if (data.comando === 'clipe' && data.url_video) {{
                                if (data.token_unico !== ultimoTokenProcessado) {{
                                    ultimoTokenProcessado = data.token_unico;
                                    
                                    tituloRep.innerText = "▶️ Reproduzindo: " + (data.musica || "Vídeo");
                                    msgStatus.style.display = 'none';
                                    vid.style.display = 'block';
                                    barraControlo.style.display = 'flex';

                                    vid.src = data.url_video;
                                    vid.currentTime = 0;
                                    vid.play().catch(e => console.log("Erro ao reproduzir:", e));
                                }}
                            }} else {{
                                // Se estiver parado ou limpo
                                if (vid.src) {{
                                    vid.pause();
                                    vid.src = "";
                                    vid.style.display = 'none';
                                    barraControlo.style.display = 'none';
                                    msgStatus.style.display = 'block';
                                    tituloRep.innerText = "Aguardando seleção...";
                                }}
                            }}
                        }})
                        .catch(err => console.log("Erro de rede:", err));
                }}

                // Quando o clipe acaba, limpa o Firebase autonomamente sem recarregar o Streamlit
                vid.onended = function() {{
                    vid.pause();
                    vid.src = "";
                    vid.style.display = 'none';
                    barraControlo.style.display = 'none';
                    msgStatus.style.display = 'block';
                    tituloRep.innerText = "Clipe concluído. A aguardar...";

                    fetch(urlStatus, {{
                        method: 'PUT',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            "comando": "parar",
                            "cantor": "",
                            "musica": "",
                            "url_video": "",
                            "token_unico": "fim_" + Date.now()
                        }})
                    }});
                }};

                vid.ontimeupdate = function() {{
                    if (vid.duration) {{
                        document.getElementById('barraSeek').value = (vid.currentTime / vid.duration) * 100;
                        let min = Math.floor(vid.currentTime / 60);
                        let seg = Math.floor(vid.currentTime % 60);
                        document.getElementById('txtTempo').innerText = (min < 10 ? "0" + min : min) + ":" + (seg < 10 ? "0" + seg : seg);
                    }}
                }};

                function controlarPlay() {{
                    if (vid.paused) {{
                        vid.play();
                        document.getElementById('btnPlayPause').innerText = "⏸️";
                    }} else {{
                        vid.pause();
                        document.getElementById('btnPlayPause').innerText = "▶️";
                    }}
                }}

                function ajustarSeek(val) {{
                    if (vid.duration) {{
                        vid.currentTime = (val * vid.duration) / 100;
                    }}
                }}

                function ajustarAudio() {{
                    vid.muted = !vid.muted;
                    document.getElementById('btnAudio').innerText = vid.muted ? "🔇" : "🔊";
                }}

                // Verifica o Firebase a cada 2 segundos sem refrescar a página inteira
                setInterval(verificarEstadoFirebase, 2000);
                verificarEstadoFirebase();
            </script>
        </body>
        </html>
        """
        components.html(painel_autonomo_html, height=350, scrolling=False)
