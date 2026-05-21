import yaml
import os
import streamlit as st
import bcrypt
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

CONFIG_PATH = "config.yaml"

def load_config():
    config_str = os.getenv("CONFIG_YAML")
    if config_str:
        return yaml.safe_load(config_str)
    with open(CONFIG_PATH) as file:
        return yaml.load(file, Loader=SafeLoader)

def save_config(config):
    if not os.getenv("CONFIG_YAML"):
        with open(CONFIG_PATH, "w") as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True)

def get_authenticator():
    config = load_config()
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config.get("preauthorized", [])
    )
    return authenticator, config

def check_session():
    if st.session_state.get("authentication_status"):
        return True

    # Intentar leer cookie
    try:
        authenticator, config = get_authenticator()
        authenticator.login("Login", "unrendered")
        if st.session_state.get("authentication_status"):
            return True
    except:
        pass

    return False

def clear_session_cookie():
    st.session_state["authentication_status"] = False
    st.session_state["username"] = None
    st.session_state["name"]     = None

def register_user(nombre, username, email, password):
    config = load_config()
    if username in config["credentials"]["usernames"]:
        return False, "Ese nombre de usuario ya existe."
    for user_data in config["credentials"]["usernames"].values():
        if user_data.get("email") == email:
            return False, "Ese email ya está registrado."
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    config["credentials"]["usernames"][username] = {
        "email":    email,
        "name":     nombre,
        "password": hashed,
    }
    save_config(config)
    return True, "¡Cuenta creada exitosamente!"

def login_page():
    authenticator, config = get_authenticator()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #0f1117; color: #e8eaf0; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stToolbar"]    { display: none !important; }
    [data-testid="stSidebar"]    { display: none !important; }
    [data-testid="stForm"] {
        background: #161b27 !important;
        border: 1px solid #1e2535 !important;
        border-radius: 16px !important;
        padding: 24px !important;
    }
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important;
        border-radius: 10px !important;
        color: white !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    input {
        background-color: #1a1f2e !important;
        border-color: #2a3347 !important;
        border-radius: 8px !important;
        color: #e8eaf0 !important;
    }
    [data-testid="stWidgetLabel"] p {
        color: #9ca3af !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }
    [data-baseweb="tab-list"] {
        background: #0f1117 !important;
        border-bottom: 1px solid #1e2535 !important;
        border-radius: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }
    [data-baseweb="tab"] {
        background: transparent !important;
        border-bottom: 2px solid transparent !important;
        color: #6b7280 !important;
        font-size: 0.88rem !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
    }
    [aria-selected="true"] {
        background: transparent !important;
        border-bottom: 2px solid #6366f1 !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; padding: 48px 0 32px 0'>
        <div style='font-family:DM Mono,monospace; font-size:2.2rem; font-weight:600; color:#fff'>
            maicro<span style='color:#6366f1'>track</span>
        </div>
        <div style='color:#6b7280; font-size:0.85rem; margin-top:8px'>
            Tu tracker de macros y micronutrientes con IA
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])

    with col_c:
        tab_login, tab_registro = st.tabs(["🔑 Iniciar sesión", "✨ Crear cuenta"])

        with tab_login:
            name, authentication_status, username = authenticator.login("Login", "main")

            if authentication_status:
                st.session_state["authentication_status"] = True
                st.session_state["username"] = username
                st.session_state["name"]     = name
                st.rerun()
            elif authentication_status is False:
                st.error("Usuario o contraseña incorrectos.")

        with tab_registro:
            with st.form("form_registro"):
                nombre       = st.text_input("Nombre completo")
                username_reg = st.text_input("Nombre de usuario", placeholder="sin espacios, ej: juan123")
                email        = st.text_input("Email")
                password     = st.text_input("Contraseña", type="password")
                password2    = st.text_input("Repetir contraseña", type="password")

                if st.form_submit_button("✨ Crear cuenta", use_container_width=True, type="primary"):
                    if not nombre or not username_reg or not email or not password:
                        st.warning("Completá todos los campos.")
                    elif " " in username_reg:
                        st.warning("El usuario no puede tener espacios.")
                    elif len(password) < 6:
                        st.warning("La contraseña debe tener al menos 6 caracteres.")
                    elif password != password2:
                        st.warning("Las contraseñas no coinciden.")
                    else:
                        ok, mensaje = register_user(nombre, username_reg, email, password)
                        if ok:
                            st.success(mensaje)
                            st.info("Ya podés iniciar sesión en la pestaña de arriba.")
                        else:
                            st.error(mensaje)

    return authenticator