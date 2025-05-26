# auth.py
import streamlit as st
import base64
from io import BytesIO
from PIL import Image
from utils.encoded_image import encoded_image

USUARIOS = {
    "tecnico": "senha123"
}

def tela_login():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            image_data = base64.b64decode(encoded_image)
            image = Image.open(BytesIO(image_data))
            st.image(image, width=400)
        except Exception as e:
            st.warning("⚠️ Erro ao carregar a imagem.")
            st.text(f"Detalhes: {e}")

        st.markdown("## 🔐 Login")
        st.write("Entre com suas credenciais para continuar.")

        with st.form("form_login"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            entrar = st.form_submit_button("Entrar")

            if entrar:
                if usuario in USUARIOS and USUARIOS[usuario] == senha:
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = usuario
                    st.success(f"✅ Bem-vindo, {usuario}!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha inválidos.")
