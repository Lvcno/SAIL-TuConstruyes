import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SAIL 3.0 - Gestión de Leads", page_icon=None, layout="centered")

# --- 🎨 INYECCIÓN DE CSS PERSONALIZADO (PROLIJO, FILOSO Y SIN CORTES) ---
estilo_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
}

.stApp {
    background-color: #D91A1A !important;
}

/* ENCABEZADOS DE CASILLAS */
div[data-testid="stWidgetLabel"] p {
    color: white !important;
    font-weight: 500 !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* --- CORRECCIÓN DE CASILLAS: TOTALMENTE CUADRADAS Y MÁS ALTAS --- */
div[data-baseweb="input"], 
div[data-baseweb="input"] > div, 
div[data-baseweb="select"] > div, 
div[data-baseweb="textarea"] > div,
div[data-baseweb="textarea"] {
    background-color: #ffffff !important;
    border: none !important;
    border-radius: 0px !important; /* Fuerza el borde cuadrado */
    min-height: 55px !important; /* Aumentamos altura para que no se corte */
}

/* --- AJUSTE DE TEXTO: PROLIJO Y ALINEADO --- */
div[data-baseweb="input"] input {
    color: #333333 !important; 
    font-weight: 500 !important; 
    -webkit-text-fill-color: #333333 !important;
    text-align: left !important;
    padding-left: 15px !important;
    font-size: 1.1rem !important;
    height: 55px !important; /* Centrado vertical manual */
    line-height: 55px !important;
}

textarea, textarea[data-baseweb="textarea"] {
    color: #333333 !important;
    font-weight: 500 !important;
    -webkit-text-fill-color: #333333 !important;
    padding: 15px !important;
}

/* SELECTORES (ASIGNAR A / CANAL) */
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #333333 !important; 
    font-weight: 500 !important;
    -webkit-text-fill-color: #333333 !important;
    text-align: left !important;
}

/* BOTÓN PROCESAR */
div.stButton > button:first-child {
    background-color: #ffffff !important;
    color: #D91A1A !important;
    border-radius: 0px !important;
    border: none !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    padding: 15px !important;
    height: 60px !important;
}

/* CAJA DE MENSAJE (BLANCO Y NEGRO) */
div[data-testid="stCodeBlock"] {
    background-color: #ffffff !important;
    border-radius: 0px !important;
    border: 1px solid #ffffff !important;
}
div[data-testid="stCodeBlock"] code {
    color: #000000 !important;
    font-weight: 600 !important;
}
</style>
"""
st.markdown(estilo_css, unsafe_allow_html=True)

# --- LOGO DE LA EMPRESA ---
# Asegúrate de que el archivo se llame exactamente logo.png y esté en GitHub
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    st.markdown("<h1 style='color: white; text-align: center;'>TU CONSTRUYES</h1>", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS (MODO NUBE) ---
def conectar_control_mk():
    # Cuando lo subas a la nube, esto leerá los Secrets
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("Control de Leads y Cierres").worksheet("Control MK")
    except:
        # Respaldo local para pruebas en tu Mac
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
        client = gspread.authorize(creds)
        return client.open("Control de Leads y Cierres").worksheet("Control MK")

EQUIPO = ["Lysset", "Daniel", "John", "Danitza", "Matías", "N/A"]

if 'indice_vendedor' not in st.session_state:
    st.session_state.indice_vendedor = 0

# --- FORMULARIO ---
with st.form("registro_base", clear_on_submit=True):
    vendedor_final = st.selectbox("ASIGNAR A:", options=EQUIPO, index=st.session_state.indice_vendedor)
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("NOMBRE CLIENTE")
        telefono = st.text_input("TELÉFONO (569...)")
        correo = st.text_input("CORREO")
    with col2:
        producto_msg = st.text_input("PRODUCTO DE INTERÉS")
        # ACTUALIZADO: WEB y Sucursal agregados
        canal = st.selectbox("CANAL", ["Cliengo", "Llamada", "WhatsApp", "WEB", "Sucursal"])
        detalle = st.text_area("DETALLE ADICIONAL")

    submit = st.form_submit_button("🚀 PROCESAR Y GUARDAR", use_container_width=True)

if submit:
    if nombre and telefono:
        try:
            with st.spinner("Registrando..."):
                ws = conectar_control_mk()
                columna_c = ws.col_values(3)
                fila_destino = 8 # Empieza después del encabezado oficial
                
                for i in range(len(columna_c) - 1, -1, -1):
                    if columna_c[i].strip() != "":
                        fila_destino = i + 2 
                        break
                
                fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
                fila_base = [nombre, correo, telefono, fecha_hora, canal, vendedor_final]
                ws.update(range_name=f"C{fila_destino}:H{fila_destino}", values=[fila_base], value_input_option="USER_ENTERED")
                
                # MENSAJE PARA EL VENDEDOR (CONTACTAR AHORA)
                link_wsp = f"https://wa.me/{telefono.replace(' ', '').replace('+', '')}"
                msg = f"""🌟 *¡NUEVO LEAD ASIGNADO!* 🌟

👤 *CLIENTE:* {nombre}
🏗️ *INTERÉS:* {producto_msg}
📧 *EMAIL:* {correo if correo else "N/A"}
💬 *DETALLE:* {detalle}

👉 *CONTACTAR AHORA:*
📱 {link_wsp}
-------------------------------------------
🚀 *Asignado a:* @{vendedor_final}
¡Mucho éxito! 🎯"""

                st.markdown("<p style='color: white; font-weight: 700; margin-top: 15px;'>COPIA EL MENSAJE PARA EL VENDEDOR:</p>", unsafe_allow_html=True)
                st.code(msg, language="text")
                st.session_state.indice_vendedor = (EQUIPO.index(vendedor_final) + 1) % len(EQUIPO)

        except Exception as e:
            st.error(f"Error: Revisa la conexión o las credenciales.")
    else:
        st.warning("⚠️ Ingresa Nombre y Teléfono.")