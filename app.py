import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SAIL 3.0 - Gestión de Leads", page_icon=None, layout="centered")

# --- 🎨 CSS PROLIJO (AJUSTADO PARA TODO TIPO DE PANTALLAS Y TEXTOS) ---
estilo_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.stApp { background-color: #D91A1A !important; }

/* Evita que el formulario se estire feo en computadores grandes */
.block-container { max-width: 850px !important; padding-top: 2rem !important; }

div[data-testid="stWidgetLabel"] p {
    color: white !important; font-weight: 500 !important; text-transform: uppercase; font-size: 0.9rem !important;
}

/* Casillas Cuadradas y Prolijas */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div {
    background-color: #ffffff !important; border-radius: 0px !important; min-height: 48px !important; border: none !important;
}

/* Texto general dentro de las casillas */
div[data-baseweb="input"] input, textarea {
    color: #333333 !important; font-weight: 500 !important; -webkit-text-fill-color: #333333 !important;
    padding-left: 15px !important; line-height: 1.5 !important;
}

/* --- SOLUCIÓN PARA SELECTORES EN BLANCO --- */
div[data-baseweb="select"] span, div[data-baseweb="select"] div {
    color: #333333 !important; font-weight: 500 !important; -webkit-text-fill-color: #333333 !important; 
    text-align: left !important;
}

/* Color de las opciones al abrir el menú desplegable */
ul[data-baseweb="menu"] li, ul[data-baseweb="menu"] span {
    color: #333333 !important; font-weight: 500 !important;
}

/* Color de la flecha del selector */
div[data-baseweb="select"] svg {
    fill: #333333 !important;
}

/* Botón Procesar */
div.stButton > button:first-child {
    background-color: #ffffff !important; color: #D91A1A !important; border-radius: 0px !important;
    font-weight: 700 !important; text-transform: uppercase; width: 100%; height: 50px !important;
}

/* Caja de mensaje prolija */
div[data-testid="stCodeBlock"] { background-color: #ffffff !important; border-radius: 0px !important; }
div[data-testid="stCodeBlock"] code { color: #000000 !important; font-weight: 600 !important; }
</style>
"""
st.markdown(estilo_css, unsafe_allow_html=True)

# --- LOGO CENTRADO ---
try:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)
except:
    st.markdown("<h2 style='color: white; text-align: center;'>TU CONSTRUYES</h2>", unsafe_allow_html=True)

# --- CONEXIÓN DE SEGURIDAD (NUBE) ---
def conectar_control_mk():
    # Usa los Secrets que pegaremos en la web
    creds_dict = dict(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Control de Leads y Cierres").worksheet("Control MK")

EQUIPO = ["Lysset", "Daniel", "John", "Danitza", "Matías", "N/A"]
if 'indice_vendedor' not in st.session_state: st.session_state.indice_vendedor = 0

# --- FORMULARIO REORGANIZADO (LÓGICA HUMANA) ---
with st.form("registro_base", clear_on_submit=True):
    # Asignación siempre arriba
    vendedor_final = st.selectbox("ASIGNAR A:", options=EQUIPO, index=st.session_state.indice_vendedor)
    
    # FILA 1: Contacto Rápido
    c_contacto1, c_contacto2 = st.columns(2)
    nombre = c_contacto1.text_input("NOMBRE CLIENTE")
    telefono = c_contacto2.text_input("TELÉFONO (Sin +569)", placeholder="Ej: 912345678")
    
    # FILA 2: Datos Secundarios
    c_canal1, c_canal2 = st.columns(2)
    correo = c_canal1.text_input("CORREO", placeholder="ejemplo@correo.com")
    canal = c_canal2.selectbox("CANAL", ["Cliengo", "Llamada", "WhatsApp", "WEB", "Sucursal"])
    
    # FILA 3: Comercial (Ancho completo para escribir cómodo)
    producto = st.text_input("PRODUCTO DE INTERÉS", placeholder="Ej: Planchas OSB, PV4...")
    
    # FILA 4: Detalle (Ancho completo y más alto)
    detalle = st.text_area("DETALLE ADICIONAL", height=100, placeholder="Escribe aquí notas importantes...")

    # Botón ancho completo al final
    submit = st.form_submit_button("🚀 PROCESAR Y GUARDAR")

if submit:
    if nombre and telefono:
        try:
            with st.spinner("Guardando en Control de Leads y Cierres..."):
                ws = conectar_control_mk()
                columna_c = ws.col_values(3)
                fila_destino = max(len(columna_c) + 1, 8)
                
                fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                # --- GUARDAMOS SOLO HASTA COLUMNA H ---
                fila_base = [nombre, correo, telefono, fecha_hora, canal, vendedor_final]
                ws.update(range_name=f"C{fila_destino}:H{fila_destino}", values=[fila_base], value_input_option="USER_ENTERED")
                
                # --- MENSAJE WHATSAPP ---
                link_wsp = f"https://wa.me/{telefono.replace(' ', '').replace('+', '')}"
                msg = f"🌟 *¡NUEVO LEAD ASIGNADO!* 🌟\n\n👤 *CLIENTE:* {nombre}\n🏗️ *INTERÉS:* {producto}\n📧 *EMAIL:* {correo if correo else 'N/A'}\n💬 *DETALLE:* {detalle}\n\n👉 *CONTACTAR AHORA:*\n📱 {link_wsp} \n🚀 *Asignado a:* @{vendedor_final}\n¡Mucho éxito! 🎯"
                st.markdown("<p style='color: white; font-weight: 700; margin-top: 15px;'>COPIA EL MENSAJE:</p>", unsafe_allow_html=True)
                st.code(msg, language="text")
                
                # Rotar vendedor
                st.session_state.indice_vendedor = (EQUIPO.index(vendedor_final) + 1) % len(EQUIPO)
        except Exception as e: 
            st.error(f"Error: {e}")
    else: 
        st.warning("⚠️ Nombre y Teléfono obligatorios.")
