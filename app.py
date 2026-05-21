import streamlit as st
from datetime import datetime, timedelta
from database import init_db, SessionLocal
from models import Meal, MacroGoal
from foods import ALIMENTOS
from ai_parser import interpretar_comida
from calculator import calcular_macros
from suggestions import sugerir_comidas, reemplazar_plato
from nav import navbar
from auth import login_page, check_session

init_db()

# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────

if not check_session():
    login_page()
    st.stop()

user_id = st.session_state.get("username")

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #0f1117; color: #e8eaf0; }
[data-testid="stSidebar"] { background-color: #161b27; border-right: 1px solid #1e2535; min-width: 260px !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
h1 { font-size: 1.8rem !important; font-weight: 600 !important; color: #ffffff !important; letter-spacing: -0.5px; }
h2, h3 { font-size: 1rem !important; font-weight: 600 !important; color: #ffffff !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; margin-top: 8px !important; }
[data-baseweb="tab-list"] { background: #0f1117 !important; border-bottom: 1px solid #1e2535 !important; border-radius: 0 !important; padding: 0 !important; gap: 0 !important; }
[data-baseweb="tab"] { background: transparent !important; border-radius: 0 !important; border-bottom: 2px solid transparent !important; color: #6b7280 !important; font-size: 0.88rem !important; padding: 10px 20px !important; font-weight: 500 !important; }
[aria-selected="true"] { background: transparent !important; border-bottom: 2px solid #6366f1 !important; color: #ffffff !important; }
[data-testid="stForm"] { background: #161b27 !important; border: 1px solid #1e2535 !important; border-radius: 16px !important; padding: 24px !important; }
[data-baseweb="select"] > div { background: #1a1f2e !important; border: 1px solid #2a3347 !important; border-radius: 10px !important; }
[data-baseweb="input"] { background: #1a1f2e !important; border: 1px solid #2a3347 !important; border-radius: 10px !important; }
[data-testid="stNumberInput"] input { background: #1a1f2e !important; border-radius: 10px !important; }
[data-testid="stWidgetLabel"] p { color: #9ca3af !important; font-size: 0.82rem !important; font-weight: 500 !important; text-transform: uppercase !important; letter-spacing: 0.04em !important; }
[data-testid="stMetric"] { background: #161b27; border: 1px solid #1e2535; border-radius: 12px; padding: 16px !important; }
[data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #6b7280 !important; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { font-family: 'DM Mono', monospace !important; font-size: 1.6rem !important; color: #ffffff !important; }
[data-testid="stMetricDelta"] { font-size: 0.75rem !important; color: #6b7280 !important; }
[data-testid="stFormSubmitButton"] > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; border: none !important; border-radius: 10px !important; color: white !important; font-weight: 600 !important; font-size: 0.88rem !important; padding: 0.6rem 1.5rem !important; width: 100% !important; margin-top: 8px !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; border: none !important; border-radius: 10px !important; color: white !important; font-weight: 600 !important; }
.stButton > button { background: #1e2535 !important; border: 1px solid #2a3347 !important; border-radius: 10px !important; color: #c8ccd8 !important; }
[data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; border-radius: 99px !important; }
[data-testid="stProgressBar"] > div { background-color: #1e2535 !important; border-radius: 99px !important; height: 6px !important; }
[data-testid="stExpander"] { background: #161b27 !important; border: 1px solid #1e2535 !important; border-radius: 12px !important; }
[data-testid="stExpander"] summary { color: #c8ccd8 !important; font-weight: 500 !important; }
hr { border-color: #1e2535 !important; }
[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; }
div[data-testid="column"] .stButton > button { font-size: 0.75rem !important; padding: 0.3rem 0.6rem !important; height: auto !important; }
.stApp { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0px); } }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────

MICRO_KEYS = [
    "magnesio_mg", "zinc_mg", "hierro_mg", "calcio_mg", "potasio_mg",
    "sodio_mg", "vitamina_c_mg", "vitamina_d_iu", "vitamina_b12_mcg", "omega3_g"
]

MICRO_LABELS = {
    "magnesio_mg":      {"label": "Magnesio",    "unidad": "mg",  "goal": 400,  "emoji": "🪨"},
    "zinc_mg":          {"label": "Zinc",         "unidad": "mg",  "goal": 11,   "emoji": "⚡"},
    "hierro_mg":        {"label": "Hierro",       "unidad": "mg",  "goal": 18,   "emoji": "🔴"},
    "calcio_mg":        {"label": "Calcio",       "unidad": "mg",  "goal": 1000, "emoji": "🦴"},
    "potasio_mg":       {"label": "Potasio",      "unidad": "mg",  "goal": 3500, "emoji": "🍌"},
    "sodio_mg":         {"label": "Sodio",        "unidad": "mg",  "goal": 2300, "emoji": "🧂"},
    "vitamina_c_mg":    {"label": "Vitamina C",   "unidad": "mg",  "goal": 90,   "emoji": "🍊"},
    "vitamina_d_iu":    {"label": "Vitamina D",   "unidad": "UI",  "goal": 600,  "emoji": "☀️"},
    "vitamina_b12_mcg": {"label": "Vitamina B12", "unidad": "mcg", "goal": 2.4,  "emoji": "💊"},
    "omega3_g":         {"label": "Omega 3",      "unidad": "g",   "goal": 1.6,  "emoji": "🐟"},
}

# ─────────────────────────────────────────
# FUNCIONES DE BASE DE DATOS
# ─────────────────────────────────────────

def get_or_create_goal():
    db   = SessionLocal()
    goal = db.query(MacroGoal).filter(MacroGoal.user_id == user_id).first()
    if not goal:
        goal = MacroGoal(user_id=user_id)
        db.add(goal)
        db.commit()
        db.refresh(goal)
    db.close()
    return goal

def update_goal(calories, protein, carbs, fats):
    db   = SessionLocal()
    goal = db.query(MacroGoal).filter(MacroGoal.user_id == user_id).first()
    if not goal:
        goal = MacroGoal(user_id=user_id)
        db.add(goal)
    goal.calories = calories
    goal.protein  = protein
    goal.carbs    = carbs
    goal.fats     = fats
    db.commit()
    db.close()

def create_meal(meal_type, description, calories, protein, carbs, fats, micros=None):
    db   = SessionLocal()
    meal = Meal(user_id=user_id, meal_type=meal_type, description=description,
                calories=calories, protein=protein, carbs=carbs, fats=fats)
    if micros:
        for key in MICRO_KEYS:
            setattr(meal, key, micros.get(key, 0))
    db.add(meal)
    db.commit()
    db.close()

def get_today_meals():
    db    = SessionLocal()
    today = datetime.now().date()
    meals = db.query(Meal).filter(Meal.user_id == user_id).order_by(Meal.created_at.desc()).all()
    result = [m for m in meals if m.created_at.date() == today]
    db.close()
    return result

def delete_meal(meal_id):
    db   = SessionLocal()
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == user_id).first()
    if meal:
        db.delete(meal)
        db.commit()
    db.close()

def get_totals_today():
    meals  = get_today_meals()
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
    for key in MICRO_KEYS:
        totals[key] = 0
    for meal in meals:
        totals["calories"] += meal.calories or 0
        totals["protein"]  += meal.protein  or 0
        totals["carbs"]    += meal.carbs    or 0
        totals["fats"]     += meal.fats     or 0
        for key in MICRO_KEYS:
            totals[key] += getattr(meal, key, 0) or 0
    return totals

def get_all_meals():
    db    = SessionLocal()
    meals = db.query(Meal).filter(Meal.user_id == user_id).order_by(Meal.created_at).all()
    db.close()
    return meals

def cumplimiento(actual, objetivo):
    if objetivo <= 0:
        return 0
    return min(actual / objetivo * 100, 100)

def badge(pct):
    if pct >= 90:
        return "#22c55e", "✅"
    elif pct >= 60:
        return "#f59e0b", "⚠️"
    else:
        return "#ef4444", "❌"

def calcular_racha(all_meals):
    if not all_meals:
        return 0
    fechas = sorted(set(m.created_at.date() for m in all_meals), reverse=True)
    hoy    = datetime.now().date()
    if fechas[0] != hoy and fechas[0] != hoy - timedelta(days=1):
        return 0
    racha  = 0
    inicio = hoy if fechas[0] == hoy else hoy - timedelta(days=1)
    for i in range(len(fechas)):
        if fechas[i] == inicio - timedelta(days=i):
            racha += 1
        else:
            break
    return racha

# ─────────────────────────────────────────
# PÁGINA CONFIG
# ─────────────────────────────────────────

st.set_page_config(page_title="MaicroTrack", page_icon="🥗", layout="wide")
navbar("app")

st.markdown(f"""
<div style='text-align:right; margin-top:-20px; margin-bottom:16px; color:#6b7280; font-size:0.85rem; font-family:DM Mono,monospace'>
    {datetime.now().strftime("%A %d %b %Y")}
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# INICIALIZAR PÁGINA
# ─────────────────────────────────────────

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "calculadora"

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style='background:#1e2535; border-radius:10px; padding:10px 14px; margin-bottom:10px; display:flex; align-items:center; gap:8px'>
        <span style='font-size:1.2rem'>👤</span>
        <div>
            <div style='color:#fff; font-size:0.85rem; font-weight:500'>{st.session_state.get("name", user_id)}</div>
            <div style='color:#6b7280; font-size:0.72rem'>{user_id}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Cerrar sesión", use_container_width=True, key="btn_cerrar_sesion"):
        from auth import clear_session_cookie
        clear_session_cookie()
        st.rerun()

    st.divider()

    pagina_actual = st.session_state["pagina"]

    if st.button("🧮 Calculadora", use_container_width=True, type="primary" if pagina_actual == "calculadora" else "secondary", key="btn_calculadora"):
        st.session_state["pagina"] = "calculadora"
        st.rerun()
    if st.button("🥗 Tracker", use_container_width=True, type="primary" if pagina_actual == "tracker" else "secondary", key="btn_tracker"):
        st.session_state["pagina"] = "tracker"
        st.rerun()
    if st.button("⚙️ Ajustes", use_container_width=True, type="primary" if pagina_actual == "ajustes" else "secondary", key="btn_ajustes"):
        st.session_state["pagina"] = "ajustes"
        st.rerun()
    if st.button("📧 Contacto", use_container_width=True, type="primary" if pagina_actual == "contacto" else "secondary", key="btn_contacto"):
        st.session_state["pagina"] = "contacto"
        st.rerun()
    if st.button("💪 Personalizá tu rutina", use_container_width=True, type="primary" if pagina_actual == "rutina" else "secondary", key="btn_rutina"):
        st.session_state["pagina"] = "rutina"
        st.rerun()
    st.divider()
    st.markdown("### 👤 Tu perfil")

    with st.expander("⚙️ Configurar perfil", expanded=False):
        with st.form("form_perfil"):
            peso      = st.number_input("Peso (kg)",   min_value=30.0,  max_value=250.0, value=75.0,  step=0.5)
            altura    = st.number_input("Altura (cm)",  min_value=100.0, max_value=250.0, value=170.0, step=1.0)
            edad      = st.number_input("Edad",         min_value=10,    max_value=100,   value=25,    step=1)
            sexo      = st.selectbox("Sexo", ["Masculino", "Femenino"])
            actividad = st.selectbox("Nivel de actividad", [
                "Sedentario (sin ejercicio)",
                "Ligero (1-3 días/semana)",
                "Moderado (3-5 días/semana)",
                "Intenso (6-7 días/semana)",
                "Muy intenso (doble turno/trabajo físico)",
            ])
            objetivo = st.selectbox("Objetivo", ["Perder grasa", "Mantener", "Ganar músculo"])

            if st.form_submit_button("⚡ Calcular y guardar", use_container_width=True, type="primary"):
                macros = calcular_macros(peso, altura, edad, sexo, actividad, objetivo)
                update_goal(macros["calorias"], macros["proteina"], macros["carbos"], macros["grasas"])
                st.success("¡Objetivos actualizados!")
                st.rerun()

    st.divider()
    goal_actual = get_or_create_goal()
    st.markdown("**🎯 Objetivos actuales**")
    st.markdown(f"""
    <div style='display:flex; flex-direction:column; gap:8px; margin-top:8px'>
        <div style='background:#1e2535; border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.8rem'>🔥 Calorías</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.9rem'>{goal_actual.calories:.0f} kcal</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.8rem'>🥩 Proteína</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.9rem'>{goal_actual.protein:.0f}g</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.8rem'>🍚 Carbos</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.9rem'>{goal_actual.carbs:.0f}g</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.8rem'>🥑 Grasas</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.9rem'>{goal_actual.fats:.0f}g</span>
        </div>
    </div>
    <div style='margin-top:14px; margin-bottom:6px; color:#6b7280; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em'>
        🧬 Micros — objetivos diarios
    </div>
    <div style='display:flex; flex-direction:column; gap:6px'>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>🪨 Magnesio</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>400 mg</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>⚡ Zinc</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>11 mg</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>🔴 Hierro</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>18 mg</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>🦴 Calcio</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>1000 mg</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>🍌 Potasio</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>3500 mg</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>🧂 Sodio</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>2300 mg</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>🍊 Vitamina C</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>90 mg</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>☀️ Vitamina D</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>600 UI</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>💊 Vitamina B12</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>2.4 mcg</span>
        </div>
        <div style='background:#1e2535; border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between'>
            <span style='color:#6b7280; font-size:0.78rem'>🐟 Omega 3</span>
            <span style='color:#fff; font-family:DM Mono,monospace; font-size:0.8rem'>1.6 g</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# CONTENIDO PRINCIPAL
# ─────────────────────────────────────────

pagina = st.session_state["pagina"]

# ══════════════════════════════════════════
# PÁGINA: TRACKER
# ══════════════════════════════════════════

if pagina == "calculadora":

    st.divider()
    st.subheader("➕ Cargar comida")

    tab1, tab2, tab3 = st.tabs(["🤖 Describir con IA", "📋 Elegir de lista", "💊 Suplementos"])

    with tab1:
        with st.form("form_ia"):
            tipo_ia = st.selectbox("Tipo de comida", ["Desayuno", "Almuerzo", "Merienda", "Cena", "Snack"], key="tipo_ia")
            texto   = st.text_input("Describí lo que comiste", placeholder="Ej: 100g de atún con 4 panes lactales")
            interpretar = st.form_submit_button("🔍 Interpretar", use_container_width=True, type="primary")

        if interpretar:
            if not texto:
                st.warning("Escribí algo primero.")
            else:
                with st.spinner("Interpretando con IA..."):
                    try:
                        datos = interpretar_comida(texto)
                        st.session_state["preview"] = {"datos": datos, "tipo": tipo_ia}
                    except Exception as e:
                        st.error(f"Error al interpretar: {e}")

        if "preview" in st.session_state:
            datos   = st.session_state["preview"]["datos"]
            tipo_ia = st.session_state["preview"]["tipo"]
            detalle = datos.get("detalle", [])

            st.markdown("""
            <div style='background:#161b27; border:1px solid #2a3347; border-radius:14px; padding:20px; margin-top:16px'>
                <div style='color:#9ca3af; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:16px'>
                    🔍 ¿Interpreté bien tu comida?
                </div>
            """, unsafe_allow_html=True)

            for item in detalle:
                st.markdown(f"""
                <div style='background:#1a1f2e; border:1px solid #2a3347; border-radius:10px; padding:12px 16px; margin-bottom:10px'>
                    <div style='color:#ffffff; font-size:0.9rem; font-weight:600; margin-bottom:8px'>{item['gramos']:.0f}g — {item['nombre']}</div>
                    <div style='display:flex; gap:16px; flex-wrap:wrap'>
                        <span style='color:#f59e0b; font-family:DM Mono,monospace; font-size:0.8rem'>🔥 {item.get('calorias', 0):.0f} kcal</span>
                        <span style='color:#6366f1; font-family:DM Mono,monospace; font-size:0.8rem'>🥩 {item.get('proteina', 0):.1f}g prot</span>
                        <span style='color:#22c55e; font-family:DM Mono,monospace; font-size:0.8rem'>🍚 {item.get('carbos', 0):.1f}g carbos</span>
                        <span style='color:#8b5cf6; font-family:DM Mono,monospace; font-size:0.8rem'>🥑 {item.get('grasas', 0):.1f}g grasas</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style='background:#1e2535; border:1px solid #6366f1; border-radius:10px; padding:12px 16px; margin-top:4px; margin-bottom:16px'>
                <div style='color:#9ca3af; font-size:0.72rem; text-transform:uppercase; margin-bottom:8px'>Total</div>
                <div style='display:flex; gap:16px; flex-wrap:wrap'>
                    <span style='color:#f59e0b; font-family:DM Mono,monospace; font-size:0.85rem; font-weight:600'>🔥 {datos['calorias']:.0f} kcal</span>
                    <span style='color:#6366f1; font-family:DM Mono,monospace; font-size:0.85rem; font-weight:600'>🥩 {datos['proteina']:.1f}g prot</span>
                    <span style='color:#22c55e; font-family:DM Mono,monospace; font-size:0.85rem; font-weight:600'>🍚 {datos['carbos']:.1f}g carbos</span>
                    <span style='color:#8b5cf6; font-family:DM Mono,monospace; font-size:0.85rem; font-weight:600'>🥑 {datos['grasas']:.1f}g grasas</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("✅ Confirmar y guardar", use_container_width=True, type="primary", key="confirm_meal"):
                    micros = {k: datos.get(k, 0) for k in MICRO_KEYS}
                    create_meal(tipo_ia, datos["descripcion"], datos["calorias"], datos["proteina"], datos["carbos"], datos["grasas"], micros)
                    del st.session_state["preview"]
                    st.success("✅ Comida guardada.")
                    st.rerun()
            with col_cancel:
                if st.button("✏️ Corregir", use_container_width=True, key="cancel_meal"):
                    del st.session_state["preview"]
                    st.rerun()

    with tab2:
        with st.form("form_lista"):
            col1, col2 = st.columns(2)
            with col1:
                tipo_lista = st.selectbox("Tipo de comida", ["Desayuno", "Almuerzo", "Merienda", "Cena", "Snack"], key="tipo_lista")
                alimento   = st.selectbox("Alimento", list(ALIMENTOS.keys()))
                gramos     = st.number_input("Gramos", min_value=1.0, value=100.0, step=10.0)
            with col2:
                datos  = ALIMENTOS[alimento]
                factor = gramos / 100
                cal = datos["calorias"] * factor
                pro = datos["proteina"] * factor
                car = datos["carbos"]   * factor
                fat = datos["grasas"]   * factor
                st.metric("🔥 Calorías", f"{cal:.0f}")
                st.metric("🥩 Proteína", f"{pro:.1f}g")
                st.metric("🍚 Carbos",   f"{car:.1f}g")
                st.metric("🥑 Grasas",   f"{fat:.1f}g")

            if st.form_submit_button("✅ Guardar comida", use_container_width=True, type="primary"):
                micros = {k: datos[k] * factor for k in MICRO_KEYS}
                create_meal(tipo_lista, f"{gramos:.0f}g de {alimento}", cal, pro, car, fat, micros)
                st.success(f"✅ {gramos:.0f}g de {alimento} guardado.")
                st.rerun()

    with tab3:
        from supplements import SUPLEMENTOS
        with st.form("form_suplemento"):
            suplemento = st.selectbox("Suplemento", list(SUPLEMENTOS.keys()))
            datos_sup  = SUPLEMENTOS[suplemento]
            cantidad   = st.number_input("Cantidad de dosis", min_value=1, max_value=10, value=1, step=1)

            st.markdown(f"""
            <div style='background:#1a1f2e; border:1px solid #2a3347; border-radius:10px; padding:12px 16px; margin-top:8px'>
                <div style='color:#9ca3af; font-size:0.75rem; margin-bottom:6px'>DOSIS: {datos_sup["dosis"]} × {cantidad}</div>
                <div style='display:flex; gap:12px; flex-wrap:wrap'>
                    <span style='color:#f59e0b; font-family:DM Mono,monospace; font-size:0.8rem'>🔥 {datos_sup["calorias"] * cantidad:.0f} kcal</span>
                    <span style='color:#6366f1; font-family:DM Mono,monospace; font-size:0.8rem'>🥩 {datos_sup["proteina"] * cantidad:.0f}g prot</span>
                </div>
            """, unsafe_allow_html=True)

            micros_texto = ""
            for k in MICRO_KEYS:
                valor = datos_sup.get(k, 0) * cantidad
                if valor > 0:
                    micros_texto += f"<span style='color:#22c55e; font-family:DM Mono,monospace; font-size:0.78rem'>{MICRO_LABELS[k]['emoji']} {valor:.1f}{MICRO_LABELS[k]['unidad']} {MICRO_LABELS[k]['label']}</span><br>"

            if micros_texto:
                st.markdown(f"<div style='margin-top:8px'>{micros_texto}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if st.form_submit_button("💊 Guardar suplemento", use_container_width=True, type="primary"):
                micros     = {k: datos_sup.get(k, 0) * cantidad for k in MICRO_KEYS}
                nombre_sup = f"{cantidad}× {suplemento}"
                create_meal("Suplemento", nombre_sup,
                            datos_sup["calorias"] * cantidad, datos_sup["proteina"] * cantidad,
                            datos_sup["carbos"] * cantidad, datos_sup["grasas"] * cantidad, micros)
                st.success(f"✅ {nombre_sup} guardado.")
                st.rerun()

    st.divider()
    st.subheader("📊 Resumen de hoy")

    goal   = get_or_create_goal()
    totals = get_totals_today()

    def progreso(actual, objetivo):
        return min(actual / objetivo, 1.0) if objetivo > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔥 Calorías", f"{totals['calories']:.0f}", f"/ {goal.calories:.0f}")
        st.progress(progreso(totals["calories"], goal.calories))
    with col2:
        st.metric("🥩 Proteína", f"{totals['protein']:.0f}g", f"/ {goal.protein:.0f}g")
        st.progress(progreso(totals["protein"], goal.protein))
    with col3:
        st.metric("🍚 Carbos", f"{totals['carbs']:.0f}g", f"/ {goal.carbs:.0f}g")
        st.progress(progreso(totals["carbs"], goal.carbs))
    with col4:
        st.metric("🥑 Grasas", f"{totals['fats']:.0f}g", f"/ {goal.fats:.0f}g")
        st.progress(progreso(totals["fats"], goal.fats))

    st.divider()
    st.subheader("🧬 Micronutrientes de hoy")

    col_a, col_b = st.columns(2)
    for i, (key, info) in enumerate(MICRO_LABELS.items()):
        actual   = totals.get(key, 0)
        objetivo = info["goal"]
        pct      = min(actual / objetivo * 100, 100) if objetivo > 0 else 0
        color    = "#22c55e" if pct >= 100 else "#f59e0b" if pct >= 60 else "#ef4444"
        estado   = "✅ Cubierto" if pct >= 100 else f"⚠️ {pct:.0f}%" if pct >= 60 else f"❌ {pct:.0f}%"

        card = (
            f"<div style='background:#161b27; border:1px solid #1e2535; border-radius:12px; padding:14px 16px; margin-bottom:10px'>"
            f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px'>"
            f"<span style='color:#c8ccd8; font-size:0.9rem'>{info['emoji']} {info['label']}</span>"
            f"<span style='color:{color}; font-size:0.8rem; font-weight:500'>{estado}</span>"
            f"</div>"
            f"<div style='color:#6b7280; font-size:0.75rem; font-family:DM Mono,monospace; margin-bottom:6px'>{actual:.1f} / {objetivo} {info['unidad']}</div>"
            f"<div style='background:#1e2535; border-radius:99px; height:5px'>"
            f"<div style='background:{color}; width:{pct:.0f}%; height:5px; border-radius:99px'></div>"
            f"</div></div>"
        )
        if i % 2 == 0:
            col_a.markdown(card, unsafe_allow_html=True)
        else:
            col_b.markdown(card, unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Comidas de hoy")

    meals = get_today_meals()
    if not meals:
        st.info("Todavía no cargaste comidas hoy.")
    else:
        for meal in meals:
            with st.expander(f"{meal.meal_type} — {meal.description} ({meal.calories:.0f} kcal)"):
                c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
                c1.metric("Calorías", f"{meal.calories:.0f}")
                c2.metric("Proteína", f"{meal.protein:.0f}g")
                c3.metric("Carbos",   f"{meal.carbs:.0f}g")
                c4.metric("Grasas",   f"{meal.fats:.0f}g")
                with c5:
                    st.markdown("<div style='padding-top:20px'>", unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar", key=f"del_{meal.id}"):
                        delete_meal(meal.id)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("💡 Plan para el resto del día")

    meals_fresh  = get_today_meals()
    totals_fresh = get_totals_today()
    goal_fresh   = get_or_create_goal()
    all_meals_db = get_all_meals()

    if "sugerencias" not in st.session_state or st.session_state.get("sugerencias_user") != user_id:
        st.session_state["sugerencias"]      = sugerir_comidas(totals_fresh, goal_fresh, MICRO_LABELS, meals_hoy=meals_fresh, all_meals=all_meals_db)
        st.session_state["sugerencias_user"] = user_id

    if "excluidos" not in st.session_state:
        st.session_state["excluidos"] = {}
    if "historial_sugerencias" not in st.session_state:
        st.session_state["historial_sugerencias"] = {}

    if st.session_state.get("sugerencias_meals_count") != len(meals_fresh):
        st.session_state["sugerencias"]           = sugerir_comidas(totals_fresh, goal_fresh, MICRO_LABELS, meals_hoy=meals_fresh, all_meals=all_meals_db)
        st.session_state["sugerencias_meals_count"] = len(meals_fresh)
        st.session_state["excluidos"]             = {}
        st.session_state["historial_sugerencias"] = {}

    sugerencias = st.session_state["sugerencias"]

    if len(sugerencias) == 1 and sugerencias[0]["tipo"] == "—":
        st.success(sugerencias[0]["nombre"])
    else:
        cols = st.columns(len(sugerencias))
        for i, sug in enumerate(sugerencias):
            with cols[i]:
                detalle_html = sug.get("detalle_html", "")
                st.markdown(
                    f"<div style='background:#161b27; border:1px solid #1e2535; border-radius:12px; padding:16px'>"
                    f"<div style='color:#6366f1; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px'>{sug['tipo']}</div>"
                    f"<div style='font-size:0.95rem; color:#ffffff; font-weight:600; margin-bottom:10px'>{sug['nombre']}</div>"
                    f"<div style='margin-bottom:10px'>{detalle_html}</div>"
                    f"<div style='font-size:0.78rem; color:#6b7280; margin-bottom:10px; line-height:1.5'>{sug['razon']}</div>"
                    f"<div style='background:#1e2535; border-radius:8px; padding:8px 12px; font-size:0.75rem; color:#6366f1; font-family:DM Mono,monospace; margin-bottom:12px'>{sug['macros']}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                hay_historial = i in st.session_state["historial_sugerencias"] and len(st.session_state["historial_sugerencias"][i]) > 0
                col_ant, col_sig = st.columns(2)

                with col_ant:
                    if st.button("← Anterior", key=f"anterior_{i}", use_container_width=True, disabled=not hay_historial):
                        anterior = st.session_state["historial_sugerencias"][i].pop()
                        if i in st.session_state["excluidos"]:
                            st.session_state["excluidos"][i].discard(anterior["nombre"])
                        st.session_state["sugerencias"][i] = anterior
                        st.rerun()

                with col_sig:
                    if st.button("Siguiente →", key=f"reemplazar_{i}", use_container_width=True):
                        if i not in st.session_state["excluidos"]:
                            st.session_state["excluidos"][i] = set()
                        if i not in st.session_state["historial_sugerencias"]:
                            st.session_state["historial_sugerencias"][i] = []

                        st.session_state["historial_sugerencias"][i].append(sug)
                        st.session_state["excluidos"][i].add(sug["nombre"])

                        nombres_otros   = {s["nombre"] for j, s in enumerate(st.session_state["sugerencias"]) if j != i}
                        todos_excluidos = st.session_state["excluidos"][i] | nombres_otros

                        nuevo = reemplazar_plato(sug["tipo"], sug["nombre"], sug["macros_dict"]["calorias"], sug["macros_dict"]["proteina"], nombres_excluidos_global=todos_excluidos)

                        if nuevo:
                            st.session_state["sugerencias"][i] = nuevo
                            st.rerun()
                        else:
                            st.session_state["historial_sugerencias"][i].pop()
                            st.session_state["excluidos"][i].discard(sug["nombre"])
                            st.toast("No hay más alternativas para este tipo de comida.")

# ══════════════════════════════════════════
# PÁGINA: HISTORIAL
# ══════════════════════════════════════════

elif pagina == "tracker":
    st.divider()

    all_meals = get_all_meals()
    goal      = get_or_create_goal()

    if not all_meals:
        st.info("Todavía no hay datos registrados.")
    else:
        hoy       = datetime.now().date()
        ultimos_7 = [hoy - timedelta(days=i) for i in range(6, -1, -1)]
        racha     = calcular_racha(all_meals)

        racha_color = "#22c55e" if racha >= 7 else "#f59e0b" if racha >= 3 else "#6366f1" if racha >= 1 else "#6b7280"
        racha_emoji = "🔥" if racha >= 1 else "💤"
        racha_texto = "¡Empezá hoy!" if racha == 0 else f"{racha} día{'s' if racha != 1 else ''} consecutivo{'s' if racha != 1 else ''}"

        st.markdown(
            f"<div style='display:flex; align-items:center; gap:10px; margin-bottom:16px'>"
            f"<span style='font-size:1.3rem'>{racha_emoji}</span>"
            f"<span style='font-family:DM Mono,monospace; font-size:1.3rem; font-weight:600; color:{racha_color}'>{racha}</span>"
            f"<span style='color:#6b7280; font-size:0.8rem'>{racha_texto}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        st.subheader("📆 Últimos 7 días")
        cols = st.columns(7)
        for i, fecha in enumerate(ultimos_7):
            meals_dia  = [m for m in all_meals if m.created_at.date() == fecha]
            totals_dia = {"calories": sum(m.calories or 0 for m in meals_dia)}
            pct        = cumplimiento(totals_dia["calories"], goal.calories)
            color, icono = badge(pct)
            es_hoy     = fecha == hoy
            borde      = "border:1px solid #6366f1;" if es_hoy else "border:1px solid #1e2535;"
            with cols[i]:
                st.markdown(
                    f"<div style='background:#161b27; {borde} border-radius:10px; padding:10px 8px; text-align:center'>"
                    f"<div style='color:#6b7280; font-size:0.7rem; margin-bottom:4px; font-family:DM Mono,monospace'>{fecha.strftime('%d/%m')}</div>"
                    f"<div style='font-size:1.2rem'>{icono}</div>"
                    f"<div style='color:{color}; font-family:DM Mono,monospace; font-size:0.75rem; margin-top:2px'>{pct:.0f}%</div>"
                    f"<div style='color:#6b7280; font-size:0.65rem'>{totals_dia['calories']:.0f} kcal</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        st.divider()
        st.subheader("🔍 Detalle por día")

        fechas    = sorted(set(m.created_at.date() for m in all_meals), reverse=True)
        fecha_sel = st.selectbox("Elegí un día", fechas, format_func=lambda f: f.strftime("%A %d de %B de %Y").capitalize())
        meals_sel = [m for m in all_meals if m.created_at.date() == fecha_sel]

        if not meals_sel:
            st.info("No hay comidas registradas para este día.")
        else:
            totals_sel = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
            for key in MICRO_KEYS:
                totals_sel[key] = 0
            for meal in meals_sel:
                totals_sel["calories"] += meal.calories or 0
                totals_sel["protein"]  += meal.protein  or 0
                totals_sel["carbs"]    += meal.carbs    or 0
                totals_sel["fats"]     += meal.fats     or 0
                for key in MICRO_KEYS:
                    totals_sel[key] += getattr(meal, key, 0) or 0

            st.markdown("##### 🍽️ Macros")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("🔥 Calorías", f"{totals_sel['calories']:.0f}", f"/ {goal.calories:.0f}")
                st.progress(cumplimiento(totals_sel["calories"], goal.calories) / 100)
            with c2:
                st.metric("🥩 Proteína", f"{totals_sel['protein']:.0f}g", f"/ {goal.protein:.0f}g")
                st.progress(cumplimiento(totals_sel["protein"], goal.protein) / 100)
            with c3:
                st.metric("🍚 Carbos", f"{totals_sel['carbs']:.0f}g", f"/ {goal.carbs:.0f}g")
                st.progress(cumplimiento(totals_sel["carbs"], goal.carbs) / 100)
            with c4:
                st.metric("🥑 Grasas", f"{totals_sel['fats']:.0f}g", f"/ {goal.fats:.0f}g")
                st.progress(cumplimiento(totals_sel["fats"], goal.fats) / 100)

            st.divider()
            st.markdown("##### 🧬 Micronutrientes")
            col_a, col_b = st.columns(2)
            for i, (key, info) in enumerate(MICRO_LABELS.items()):
                actual   = totals_sel.get(key, 0)
                objetivo = info["goal"]
                pct      = min(actual / objetivo * 100, 100) if objetivo > 0 else 0
                color, _ = badge(pct)
                card = (
                    f"<div style='background:#161b27; border:1px solid #1e2535; border-radius:10px; padding:12px 14px; margin-bottom:8px'>"
                    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px'>"
                    f"<span style='color:#c8ccd8; font-size:0.85rem'>{info['emoji']} {info['label']}</span>"
                    f"<span style='color:{color}; font-size:0.75rem; font-family:DM Mono,monospace'>{actual:.1f}/{objetivo}{info['unidad']}</span>"
                    f"</div>"
                    f"<div style='background:#1e2535; border-radius:99px; height:4px'>"
                    f"<div style='background:{color}; width:{pct:.0f}%; height:4px; border-radius:99px'></div>"
                    f"</div></div>"
                )
                if i % 2 == 0:
                    col_a.markdown(card, unsafe_allow_html=True)
                else:
                    col_b.markdown(card, unsafe_allow_html=True)

            st.divider()
            st.markdown("##### 📋 Comidas registradas")
            for meal in meals_sel:
                with st.expander(f"{meal.meal_type} — {meal.description} ({meal.calories:.0f} kcal)"):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Calorías", f"{meal.calories:.0f}")
                    c2.metric("Proteína", f"{meal.protein:.0f}g")
                    c3.metric("Carbos",   f"{meal.carbs:.0f}g")
                    c4.metric("Grasas",   f"{meal.fats:.0f}g")

# ══════════════════════════════════════════
# PÁGINA: AJUSTES
# ══════════════════════════════════════════

elif pagina == "ajustes":
    st.divider()
    st.subheader("⚙️ Ajustes")

    db            = SessionLocal()
    total_comidas = db.query(Meal).filter(Meal.user_id == user_id).count()
    total_dias    = len(set(m.created_at.date() for m in db.query(Meal).filter(Meal.user_id == user_id).all()))
    db.close()

    st.markdown("**📊 Base de datos actual**")
    c1, c2 = st.columns(2)
    c1.metric("🍽️ Comidas registradas", total_comidas)
    c2.metric("📅 Días con registro",   total_dias)

    st.divider()
    st.markdown("**🗑️ Borrar historial**")
    st.markdown("<p style='color:#6b7280'>Elimina todas las comidas. Los objetivos se mantienen.</p>", unsafe_allow_html=True)

    if "confirmar_historial" not in st.session_state:
        st.session_state.confirmar_historial = False

    if not st.session_state.confirmar_historial:
        if st.button("🗑️ Borrar todo el historial", use_container_width=True):
            st.session_state.confirmar_historial = True
            st.rerun()
    else:
        st.warning("⚠️ ¿Estás seguro? Esta acción no se puede deshacer.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, borrar historial", use_container_width=True, type="primary"):
                db = SessionLocal()
                db.query(Meal).filter(Meal.user_id == user_id).delete()
                db.commit()
                db.close()
                st.session_state.confirmar_historial = False
                st.success("✅ Historial borrado.")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_historial"):
                st.session_state.confirmar_historial = False
                st.rerun()

    st.divider()
    st.markdown("**🎯 Resetear objetivos**")
    st.markdown("<p style='color:#6b7280'>Vuelve los objetivos a los valores por defecto.</p>", unsafe_allow_html=True)

    if "confirmar_objetivos" not in st.session_state:
        st.session_state.confirmar_objetivos = False

    if not st.session_state.confirmar_objetivos:
        if st.button("🔄 Resetear objetivos", use_container_width=True):
            st.session_state.confirmar_objetivos = True
            st.rerun()
    else:
        st.warning("⚠️ ¿Estás seguro?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, resetear", use_container_width=True, type="primary", key="confirm_obj"):
                db = SessionLocal()
                db.query(MacroGoal).filter(MacroGoal.user_id == user_id).delete()
                db.commit()
                db.close()
                st.session_state.confirmar_objetivos = False
                st.success("✅ Objetivos reseteados.")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_obj"):
                st.session_state.confirmar_objetivos = False
                st.rerun()

    st.divider()
    st.markdown("**💣 Borrar todo**")
    st.markdown("<p style='color:#6b7280'>Elimina comidas y objetivos. La app queda como nueva.</p>", unsafe_allow_html=True)

    if "confirmar_todo" not in st.session_state:
        st.session_state.confirmar_todo = False

    if not st.session_state.confirmar_todo:
        if st.button("💣 Borrar todo y empezar de cero", use_container_width=True):
            st.session_state.confirmar_todo = True
            st.rerun()
    else:
        st.warning("⚠️ ¿Estás completamente seguro? Se borra TODO.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, borrar todo", use_container_width=True, type="primary", key="confirm_todo"):
                db = SessionLocal()
                db.query(Meal).filter(Meal.user_id == user_id).delete()
                db.query(MacroGoal).filter(MacroGoal.user_id == user_id).delete()
                db.commit()
                db.close()
                st.session_state.confirmar_todo = False
                st.success("✅ Todo borrado.")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_todo"):
                st.session_state.confirmar_todo = False
                st.rerun()
                
# ══════════════════════════════════════════
# PÁGINA: AJUSTES
# ══════════════════════════════════════════

elif pagina == "ajustes":
    st.divider()
    st.subheader("⚙️ Ajustes")

    db            = SessionLocal()
    total_comidas = db.query(Meal).filter(Meal.user_id == user_id).count()
    total_dias    = len(set(m.created_at.date() for m in db.query(Meal).filter(Meal.user_id == user_id).all()))
    db.close()

    st.markdown("**📊 Base de datos actual**")
    c1, c2 = st.columns(2)
    c1.metric("🍽️ Comidas registradas", total_comidas)
    c2.metric("📅 Días con registro",   total_dias)

    st.divider()
    st.markdown("**🗑️ Borrar historial**")
    st.markdown("<p style='color:#6b7280'>Elimina todas las comidas. Los objetivos se mantienen.</p>", unsafe_allow_html=True)

    if "confirmar_historial" not in st.session_state:
        st.session_state.confirmar_historial = False

    if not st.session_state.confirmar_historial:
        if st.button("🗑️ Borrar todo el historial", use_container_width=True):
            st.session_state.confirmar_historial = True
            st.rerun()
    else:
        st.warning("⚠️ ¿Estás seguro? Esta acción no se puede deshacer.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, borrar historial", use_container_width=True, type="primary"):
                db = SessionLocal()
                db.query(Meal).filter(Meal.user_id == user_id).delete()
                db.commit()
                db.close()
                st.session_state.confirmar_historial = False
                st.success("✅ Historial borrado.")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_historial"):
                st.session_state.confirmar_historial = False
                st.rerun()

    st.divider()
    st.markdown("**🎯 Resetear objetivos**")
    st.markdown("<p style='color:#6b7280'>Vuelve los objetivos a los valores por defecto.</p>", unsafe_allow_html=True)

    if "confirmar_objetivos" not in st.session_state:
        st.session_state.confirmar_objetivos = False

    if not st.session_state.confirmar_objetivos:
        if st.button("🔄 Resetear objetivos", use_container_width=True):
            st.session_state.confirmar_objetivos = True
            st.rerun()
    else:
        st.warning("⚠️ ¿Estás seguro?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, resetear", use_container_width=True, type="primary", key="confirm_obj"):
                db = SessionLocal()
                db.query(MacroGoal).filter(MacroGoal.user_id == user_id).delete()
                db.commit()
                db.close()
                st.session_state.confirmar_objetivos = False
                st.success("✅ Objetivos reseteados.")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_obj"):
                st.session_state.confirmar_objetivos = False
                st.rerun()

    st.divider()
    st.markdown("**💣 Borrar todo**")
    st.markdown("<p style='color:#6b7280'>Elimina comidas y objetivos. La app queda como nueva.</p>", unsafe_allow_html=True)

    if "confirmar_todo" not in st.session_state:
        st.session_state.confirmar_todo = False

    if not st.session_state.confirmar_todo:
        if st.button("💣 Borrar todo y empezar de cero", use_container_width=True):
            st.session_state.confirmar_todo = True
            st.rerun()
    else:
        st.warning("⚠️ ¿Estás completamente seguro? Se borra TODO.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, borrar todo", use_container_width=True, type="primary", key="confirm_todo"):
                db = SessionLocal()
                db.query(Meal).filter(Meal.user_id == user_id).delete()
                db.query(MacroGoal).filter(MacroGoal.user_id == user_id).delete()
                db.commit()
                db.close()
                st.session_state.confirmar_todo = False
                st.success("✅ Todo borrado.")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_todo"):
                st.session_state.confirmar_todo = False
                st.rerun()
            
            

# ══════════════════════════════════════════
# PÁGINA: CONTACTO
# ══════════════════════════════════════════

elif pagina == "contacto":
    st.divider()
    st.subheader("📧 Contacto")

    st.markdown("""
    <div style='background:#161b27; border:1px solid #1e2535; border-radius:14px; padding:24px; max-width:600px; margin-bottom:24px'>
        <div style='color:#c8ccd8; font-size:0.95rem; line-height:1.7'>
            ¿Necesitás asesoramiento nutricional, tenés alguna pregunta sobre la app o querés reportar un problema?
            Completá el formulario y te respondemos a la brevedad.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_contacto"):
        nombre_c = st.text_input("Nombre")
        email_c  = st.text_input("Email")
        motivo   = st.selectbox("Motivo", [
            "Consulta nutricional",
            "Problema técnico / bug",
            "Sugerencia de mejora",
            "Otro"
        ])
        mensaje  = st.text_area("Mensaje", height=150, placeholder="Escribí tu consulta acá...")

        if st.form_submit_button("📨 Enviar mensaje", use_container_width=True, type="primary"):
            if not nombre_c or not email_c or not mensaje:
                st.warning("Completá todos los campos.")
            else:
                import requests
                data = {
                    "name":    nombre_c,
                    "email":   email_c,
                    "motivo":  motivo,
                    "message": mensaje,
                }
                response = requests.post(
                    "https://formspree.io/f/xojbdjyq",
                    json=data,
                    headers={"Accept": "application/json"}
                )
                if response.status_code == 200:
                    st.success("✅ Mensaje enviado correctamente. Te respondemos a la brevedad.")
                    st.balloons()
                else:
                    st.error("❌ Hubo un error al enviar. Intentá de nuevo o escribinos directamente a juanowenbyrne@gmail.com")

                    # ══════════════════════════════════════════
# PÁGINA: RUTINA DE GIM
# ══════════════════════════════════════════

elif pagina == "rutina":
    st.divider()
    st.subheader("💪 Personalizá tu rutina de gym")

    st.markdown("""
    <div style='background:#161b27; border:1px solid #1e2535; border-radius:14px; padding:24px; max-width:600px; margin-bottom:24px'>
        <div style='color:#c8ccd8; font-size:0.95rem; line-height:1.7'>
            ¿Querés una rutina de entrenamiento personalizada según tus objetivos, nivel y disponibilidad?
            Completá el formulario y te contactamos para armar tu plan ideal.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_rutina"):
        nombre_r   = st.text_input("Nombre completo")
        email_r    = st.text_input("Email")
        telefono_r = st.text_input("Teléfono / WhatsApp", placeholder="Ej: +54 9 11 1234 5678")
        objetivo_r = st.selectbox("¿Cuál es tu objetivo?", [
            "Perder grasa",
            "Ganar músculo",
            "Mejorar resistencia",
            "Tonificar",
            "Rendimiento deportivo",
            "Salud general",
        ])
        nivel_r = st.selectbox("¿Cuál es tu nivel de entrenamiento?", [
            "Principiante (menos de 6 meses)",
            "Intermedio (6 meses a 2 años)",
            "Avanzado (más de 2 años)",
        ])
        dias_r = st.selectbox("¿Cuántos días por semana podés entrenar?", [
            "2 días", "3 días", "4 días", "5 días", "6 días"
        ])
        equipamiento_r = st.selectbox("¿Con qué equipamiento contás?", [
            "Gimnasio completo",
            "Gimnasio en casa (mancuernas, barra)",
            "Solo peso corporal",
            "Acceso limitado a equipos",
        ])
        info_extra_r = st.text_area("¿Alguna lesión o condición que debamos tener en cuenta?", height=100, placeholder="Opcional...")

        if st.form_submit_button("💪 Solicitar mi rutina personalizada", use_container_width=True, type="primary"):
            if not nombre_r or not email_r or not telefono_r:
                st.warning("Completá nombre, email y teléfono.")
            else:
                import requests
                data = {
                    "name":         nombre_r,
                    "email":        email_r,
                    "telefono":     telefono_r,
                    "objetivo":     objetivo_r,
                    "nivel":        nivel_r,
                    "dias":         dias_r,
                    "equipamiento": equipamiento_r,
                    "info_extra":   info_extra_r or "Sin observaciones",
                }
                response = requests.post(
                    "https://formspree.io/f/xojbdjyq",
                    json=data,
                    headers={"Accept": "application/json"}
                )
                if response.status_code == 200:
                    st.success("✅ ¡Solicitud enviada! Te contactamos a la brevedad para armar tu rutina personalizada.")
                    st.balloons()
                else:
                    st.error("❌ Hubo un error al enviar. Intentá de nuevo o escribinos a juanowenbyrne@gmail.com")