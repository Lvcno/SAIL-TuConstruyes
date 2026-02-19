import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SAIL 3.0 - Gestión de Leads", page_icon=None, layout="centered")

# --- 🎨 CSS LIMPIO Y SIMPLIFICADO ---
estilo_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.stApp { background-color: #D91A1A !important; }

.block-container { max-width: 850px !important; padding-top: 2rem !important; }

/* Títulos de las casillas */
div[data-testid="stWidgetLabel"] { margin-bottom: 5px !important; }
div[data-testid="stWidgetLabel"] p {
    color: white !important; font-weight: 600 !important; text-transform: uppercase; font-size: 0.9rem !important;
}

/* Color blanco para los nombres de los vendedores en los botones */
div[role="radiogroup"] label p { color: white !important; font-weight: 600 !important; font-size: 1rem !important; }

/* Casillas blancas y sin bordes */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div {
    background-color: #ffffff !important; border-radius: 0px !important; border: none !important;
}

/* --- PLAN C: CENTRADO DEFINITIVO CON FLEXBOX --- */
div[data-baseweb="input"] > div {
    display: flex !important;
    align-items: center !important; /* Alineación vertical forzada al centro */
    height: 48px !important;
}

input[type="text"] {
    color: #333333 !important; font-weight: 600 !important; -webkit-text-fill-color: #333333 !important;
    padding: 0px 15px !important; 
    margin-top: auto !important; /* Empuja por arriba */
    margin-bottom: auto !important; /* Empuja por abajo */
    line-height: normal !important;
}

/* Text area (Detalle) */
textarea {
    color: #333333 !important; font-weight: 500 !important; -webkit-text-fill-color: #333333 !important;
    padding: 15px !important; line-height: 1.5 !important;
}

/* Corrección de la lista de Canal */
div[data-baseweb="select"] span { color: #333333 !important; font-weight: 600 !important; -webkit-text-fill-color: #333333 !important; }
ul[data-baseweb="menu"] { background-color: #ffffff !important; }
ul[data-baseweb="menu"] li { background-color: #ffffff !important; color: #333333 !important; font-weight: 500 !important; }
div[data-baseweb="select"] svg { fill: #333333 !important; }

/* Estilo del botón (El ancho se controla ahora desde Python) */
div[data-testid="stFormSubmitButton"] > button {
    background-color: #ffffff !important; color: #D91A1A !important; border-radius: 0px !important;
    border: none !important; height: 55px !important; margin-top: 15px !important;
}
div[data-testid="stFormSubmitButton"] > button p {
    font-weight: 800 !important; font-size: 1.2rem !important; color: #D91A1A !important;
}
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
    creds_dict = dict(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Control de Leads y Cierres").worksheet("Control MK")

EQUIPO = ["Lysset", "Daniel", "John", "Danitza", "Matías", "N/A"]
if 'indice_vendedor' not in st.session_state: st.session_state.indice_vendedor = 0

# --- FORMULARIO REORGANIZADO ---
with st.form("registro_base", clear_on_submit=True):
    
    # --- LA SOLUCIÓN INTUITIVA: Botones en lugar de lista ---
    vendedor_final = st.radio("ASIGNAR A:", options=EQUIPO, index=st.session_state.indice_vendedor, horizontal=True)
    st.markdown("<br>", unsafe_allow_html=True) 
    
    # FILA 1
    c_contacto1, c_contacto2 = st.columns(2)
    nombre = c_contacto1.text_input("NOMBRE CLIENTE")
    telefono = c_contacto2.text_input("TELÉFONO (Sin +569)", placeholder="Ej: 912345678")
    
    # FILA 2
    c_canal1, c_canal2 = st.columns(2)
    correo = c_canal1.text_input("CORREO", placeholder="ejemplo@correo.com")
    canal = c_canal2.selectbox("CANAL", ["Cliengo", "Llamada", "WhatsApp", "WEB", "Sucursal"])
    
    # FILA 3 (Ancho completo)
    producto = st.text_input("PRODUCTO DE INTERÉS", placeholder="Ej: Planchas OSB, PV4...")
    
    # FILA 4 (Detalle alto)
    detalle = st.text_area("DETALLE ADICIONAL", height=100, placeholder="Escribe aquí notas importantes...")

    # --- BOTÓN ENVIAR LARGO ---
    submit = st.form_submit_button("ENVIAR", use_container_width=True)

if submit:
    if nombre and telefono:
        try:
            with st.spinner("Guardando en Control de Leads y Cierres..."):
                ws = conectar_control_mk()
                columna_c = ws.col_values(3)
                fila_destino = max(len(columna_c) + 1, 8)
                
                fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                # --- GUARDADO HASTA COLUMNA H ---
                fila_base = [nombre, correo, telefono, fecha_hora, canal, vendedor_final]
                ws.update(range_name=f"C{fila_destino}:H{fila_destino}", values=[fila_base], value_input_option="USER_ENTERED")
                
                # --- MENSAJE WHATSAPP ---
                link_wsp = f"https://wa.me/{telefono.replace(' ', '').replace('+', '')}"
                msg = f"🌟 *¡NUEVO LEAD ASIGNADO!* 🌟\n\n👤 *CLIENTE:* {nombre}\n🏗️ *INTERÉS:* {producto}\n📧 *EMAIL:* {correo if correo else 'N/A'}\n💬 *DETALLE:* {detalle}\n\n👉 *CONTACTAR AHORA:*\n📱 {link_wsp} \n\n🚀 *Asignado a:* @{vendedor_final}\n¡Mucho éxito! 🎯"
                st.markdown("<p style='color: white; font-weight: 700; margin-top: 15px;'>COPIA EL MENSAJE:</p>", unsafe_allow_html=True)
                st.code(msg, language="text")
                
                # Rotar vendedor
                st.session_state.indice_vendedor = (EQUIPO.index(vendedor_final) + 1) % len(EQUIPO)
                st.rerun()
        except Exception as e: 
            st.error(f"Error: {e}")
    else: 
        st.warning("⚠️ Nombre y Teléfono obligatorios.")
