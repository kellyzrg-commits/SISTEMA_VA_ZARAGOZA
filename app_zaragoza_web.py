import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import base64
import random

# --- 1. LOGIN PROFESIONAL CORREGIDO ---
def check_password():
    """Retorna True si la contraseña es correcta."""
    
    # Verificar si el secreto existe en Streamlit Cloud
    if "admin_password" not in st.secrets:
        st.error("⚠️ ERROR TÉCNICO: No has configurado 'admin_password' en los Secrets de Streamlit.")
        return False

    def password_guessed():
        # Comparación exacta
        if st.session_state["password_input"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    # Inicializar estado si no existe
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = None

    if st.session_state["password_correct"] is not True:
        st.markdown("""
            <style>
            .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); }
            .login-box {
                background-color: rgba(255, 255, 255, 0.05);
                padding: 30px; border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(12px);
                max-width: 450px; margin: auto; text-align: center;
                box-shadow: 0 15px 35px rgba(0,0,0,0.4); margin-top: 50px;
            }
            .login-title { color: white; font-family: 'Segoe UI', sans-serif; font-weight: 800; font-size: 28px; }
            .login-subtitle { color: #cbd5e1; font-size: 14px; margin-bottom: 25px; }
            </style>
            <div class="login-box">
                <div class="login-title">🏢 SISTEMA VA ZARAGOZA</div>
                <div class="login-subtitle">Gestión de Presupuestos y Aluminio</div>
            </div>
        """, unsafe_allow_html=True)

        # Input de contraseña
        st.text_input(
            "Clave de Acceso", 
            type="password", 
            on_change=password_guessed, 
            key="password_input", 
            placeholder="Escribe la contraseña y presiona Enter"
        )
        
        if st.session_state["password_correct"] is False:
            st.error("🚫 Contraseña incorrecta. Verifica mayúsculas y minúsculas.")
        
        return False
    return True

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza", page_icon="🏢", layout="wide")

if check_password():
    # --- TODO EL RESTO DE TU CÓDIGO (DB, PDF e Interfaz) ---
    ASESOR_PRINCIPAL = "Claudio Zaragoza Gorgonio"

    def conectar_db():
        try:
            return mysql.connector.connect(
                user=st.secrets.mysql.user,
                password=st.secrets.mysql.password,
                host=st.secrets.mysql.host,
                port=st.secrets.mysql.port,
                database=st.secrets.mysql.database,
                ssl_ca='ca.pem'
            )
        except Exception as err:
            st.error(f"Error de conexión: {err}")
            return None

    def guardar_registro(datos):
        conn = conectar_db()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)", (datos['folio'], datos['nombre']))
            id_cliente = cursor.lastrowid
            cursor.execute("INSERT INTO presupuestos (id_cliente, ancho, alto, importe_neto, fecha_emision) VALUES (%s, %s, %s, %s, %s)", 
                         (id_cliente, datos['ancho'], datos['alto'], datos['monto'], datetime.now().date()))
            conn.commit()
            return True
        except: return False
        finally: conn.close()

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
            self.ln(10)

    def generar_pdf_bytes(datos):
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"CLIENTE: {datos['nombre'].upper()}", 1, 1, 'L')
        pdf.cell(0, 10, f"FOLIO: {datos['folio']}", 1, 1, 'L')
        pdf.cell(0, 10, f"TOTAL: ${datos['monto']:,.2f}", 1, 1, 'L')
        return pdf.output(dest='S').encode('latin-1')

    # Interfaz
    st.markdown("<h1 style='text-align: center;'>Panel de Gestión Zaragoza</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📝 Cotizar", "📋 Historial"])

    with t1:
        with st.form("cotizador"):
            nombre = st.text_input("Nombre del Cliente")
            sistema = st.selectbox("Sistema", ["Serie 20", "Serie 35", "Eurovent", "Vidrio Templado"])
            ancho = st.number_input("Ancho (mm)", min_value=100)
            alto = st.number_input("Alto (mm)", min_value=100)
            precios = {"Serie 20": 1150, "Serie 35": 1450, "Eurovent": 2600, "Vidrio Templado": 3200}
            total = ((ancho * alto) / 1000000) * precios[sistema]
            if st.form_submit_button("Guardar"):
                if nombre:
                    folio = f"VAZ-{random.randint(1000, 9999)}"
                    d = {'nombre': nombre, 'sistema': sistema, 'ancho': ancho, 'alto': alto, 'monto': total, 'folio': folio}
                    if guardar_registro(d):
                        st.success(f"Guardado. Folio: {folio}")
                        st.download_button("Descargar PDF", generar_pdf_bytes(d), f"{folio}.pdf")

    with t2:
        conn = conectar_db()
        if conn:
            df = pd.read_sql("SELECT c.folio_vaz, c.nombre_completo, p.importe_neto, p.fecha_emision FROM presupuestos p JOIN clientes c ON p.id_cliente = c.id_cliente ORDER BY p.id_presupuesto DESC", conn)
            st.dataframe(df, use_container_width=True)
            conn.close()
