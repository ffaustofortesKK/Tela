import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TESTE DE VÍDEO", layout="wide")

st.markdown("<h1 style='color: white;'>🧪 Teste Direto de Reprodução de Vídeo</h1>", unsafe_allow_html=True)

# Link de vídeo público 100% garantido e universal em MP4
url_teste = "https://www.w3schools.com/html/mov_bbb.mp4"

st.write(f"A testar reprodução com o link direto: `{url_teste}`")

# Player HTML5 puro embutido via componente
player_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body, html {{
            margin: 0; padding: 0; width: 100%; height: 320px; background: black; overflow: hidden;
        }}
        video {{
            width: 100%; height: 320px; object-fit: contain; background: black;
        }}
    </style>
</head>
<body>
    <video id="vid-teste" controls autoplay playsinline>
        <source src="{url_teste}" type="video/mp4">
        Seu navegador não suporta a tag de vídeo.
    </video>
    <script>
        const v = document.getElementById('vid-teste');
        v.play().catch(e => {{
            v.muted = true;
            v.play();
        }});
    </script>
</body>
</html>
"""

components.html(player_html, height=330, scrolling=False)
