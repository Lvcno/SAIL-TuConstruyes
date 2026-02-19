import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SAIL 3.0 - Gestión de Leads", page_icon=None, layout="centered")

# --- 🎨 CSS PROLIJO (AJUSTADO PARA TODO TIPO DE PANTALLAS) ---
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

/* Texto dentro de las casillas */
div[data-baseweb="input"] input, div[data-baseweb="select"] span, textarea {
    color: #333333 !important; font-weight: 500 !important; -webkit-text-fill-color: #333333 !important;
    padding-left: 15px !important; line-height: 1.5 !important;
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
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Control de Leads y Cierres").worksheet("Control MK")

EQUIPO = ["Lysset", "Daniel", "John", "Danitza", "Matías", "N/A"]
if 'indice_vendedor' not in st.session_state: st.session_state.indice_vendedor = 0

# --- FORMULARIO POR FILAS ---
with st.form("registro_base", clear_on_submit=True):
    vendedor_final = st.selectbox("ASIGNAR A:", options=EQUIPO, index=st.session_state.indice_vendedor)
    
    col1, col2 = st.columns(2)
    nombre = col1.text_input("NOMBRE CLIENTE")
    producto = col2.text_input("PRODUCTO DE INTERÉS")
    
    col3, col4 = st.columns(2)
    telefono = col3.text_input("TELÉFONO (569...)")
    canal = col4.selectbox("CANAL", ["Cliengo", "Llamada", "WhatsApp", "WEB", "Sucursal"])
    
    col5, col6 = st.columns(2)
    correo = col5.text_input("CORREO")
    detalle = col6.text_area("DETALLE ADICIONAL", height=68)

    submit = st.form_submit_button("🚀 PROCESAR Y GUARDAR")

if submit:
    if nombre and telefono:
        try:
            with st.spinner("Guardando en Control de Leads y Cierres..."):
                ws = conectar_control_mk()
                columna_c = ws.col_values(3)
                fila_destino = max(len(columna_c) + 1, 8)
                
                fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
                # Fila: Nombre, Correo, Telefono, Fecha, Canal, Vendedor, Producto, Detalle
                fila_base = [nombre, correo, telefono, fecha_hora, canal, vendedor_final, producto, detalle]
                ws.update(range_name=f"C{fila_destino}:J{fila_destino}", values=[fila_base], value_input_option="USER_ENTERED")
                
                # Mensaje WhatsApp
                link_wsp = f"https://wa.me/{telefono.replace(' ', '').replace('+', '')}"
                msg = f"🌟 *¡NUEVO LEAD ASIGNADO!* 🌟\n\n👤 *CLIENTE:* {nombre}\n🏗️ *INTERÉS:* {producto}\n📧 *EMAIL:* {correo if correo else 'N/A'}\n💬 *DETALLE:* {detalle}\n\n👉 *CONTACTAR AHORA:*\n📱 {link_wsp}\n-------------------------------------------\n🚀 *Asignado a:* @{vendedor_final}\n¡Mucho éxito! 🎯"
                st.markdown("<p style='color: white; font-weight: 700; margin-top: 15px;'>COPIA EL MENSAJE:</p>", unsafe_allow_html=True)
                st.code(msg, language="text")
                st.session_state.indice_vendedor = (EQUIPO.index(vendedor_final) + 1) % len(EQUIPO)
        except Exception as e: st.error(f"Error: {e}")
    else: st.warning("⚠️ Nombre y Teléfono obligatorios.")
