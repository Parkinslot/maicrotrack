import streamlit as st
import base64

def get_logo_base64():
    with open("assets/Maicrotrack.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

def navbar(pagina_actual):
    try:
        logo_b64 = get_logo_base64()
        logo_html = f"<img src='data:image/png;base64,{logo_b64}' style='height:55px; width:auto; object-fit:contain;'>"
    except:
        logo_html = "<span style='font-family:DM Mono,monospace; font-size:1.3rem; font-weight:600; color:#fff'>maicro<span style=\"color:#6366f1\">track</span></span>"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
    .nav-container {{
        display: flex;
        align-items: center;
        padding: 0 0 24px 0;
        margin-bottom: 8px;
    }}
    </style>
    <div class='nav-container'>
        {logo_html}
    </div>
    """, unsafe_allow_html=True)