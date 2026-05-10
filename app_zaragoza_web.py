import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os
import base64
import random

# --- 1. LOGIN PROFESIONAL CON DISEÑO ---
def check_password():
    def password_guessed():
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
            }
            .login-box {
                background-color: rgba(255, 255, 255, 0.05);
                padding: 30px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(12px);
                max-width: 450px;
                margin: auto;
                text-align: center;
                box-shadow: 0 15px 35px rgba(0,0,0,0.4);
                margin-top: 50px;
            }
            .login-title {
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 800;
                font-size: 28px;
                letter-spacing: 1px;
            }
            .login-subtitle {
                color: #cbd5e1;
                font-size: 14px;
                margin-bottom: 25px;
            }
            div[data-baseweb="input"] {
                border-radius: 10px !important;
            }
            </style>
            <div class="login-box">
                <div class="login-title">🏢 SISTEMA VA ZARAGOZA</div>
                <div class="login-subtitle">Gestión de Presupuestos y Aluminio</div>
            </div>
        """, unsafe_allow_html=True)

        st.text_input("Clave de Acceso", type="password", on_change=password_guessed, key="password", placeholder="Ingresa la contraseña...")
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("🚫 Contraseña incorrecta")
        return False
    return True

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Panel", page_icon="🏢", layout="wide")

if check_password():
    # Datos fijos del negocio
    ASESOR_PRINCIPAL = "Claudio Zaragoza Gorgonio"

    # --- 2. CONEXIÓN BASE DE DATOS (Mantenida sin cambios) ---
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

    # --- 3. LÓGICA DE PERSISTENCIA ---
    def guardar_registro(datos):
        conn = conectar_db()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # Tabla Clientes
            cursor.execute("INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)", 
                         (datos['folio'], datos['nombre']))
            id_cliente = cursor.lastrowid
            
            # Tabla Presupuestos (Estructura base confirmada)
            query_pre = """
                INSERT INTO presupuestos (id_cliente, ancho, alto, importe_neto, fecha_emision) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_pre, (id_cliente, datos['ancho'], datos['alto'], datos['monto'], datetime.now().date()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Error al guardar: {e}")
            return False
        finally:
            conn.close()

    # --- 4. GENERADOR DE PDF ---
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.set_text_color(24, 46, 82)
            self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
            self.set_font('Arial', '', 9)
            self.cell(0, 5, 'Tehuacán, Puebla | Presupuesto de Obra', 0, 1, 'C')
            self.ln(10)

    def generar_pdf_bytes(datos):
        pdf = PDF()
        pdf.add_page()
        pdf.set_fill_color(24, 46, 82); pdf.set_text_color(255); pdf.set_font('Arial', 'B', 12)
        pdf.cell(130, 10, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', fill=True)
        pdf.cell(60, 10, f" FOLIO: {datos['folio']}", 1, 1, 'C', fill=True)
        
        pdf.set_text_color(0); pdf.set_font('Arial', '', 10)
        pdf.cell(130, 8, f" Fecha: {datetime.now().strftime('%d/%m/%Y')}", 1, 0, 'L')
        pdf.cell(60, 8, f" Asesor: {ASESOR_PRINCIPAL}", 1, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 10); pdf.set_fill_color(230, 230, 230)
        pdf.cell(100, 8, "SISTEMA", 1, 0, 'C', fill=True)
        pdf.cell(35, 8, "MEDIDAS (mm)", 1, 0, 'C', fill=True)
        pdf.cell(55, 8, "PRECIO NETO", 1, 1, 'C', fill=True)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(100, 12, f" {datos['sistema']}", 1, 0, 'L')
        pdf.cell(35, 12, f" {datos['ancho']} x {datos['alto']}", 1, 0, 'C')
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(55, 12, f" $ {datos['monto']:,.2f} MXN ", 1, 1, 'R')
        return pdf.output(dest='S').encode('latin-1')

    # --- 5. INTERFAZ PRINCIPAL ---
    st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🏢 Panel de Gestión Zaragoza</h1>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["📝 Crear Cotización", "📋 Historial de Ventas"])

    with t1:
        with st.form("cotizador"):
            col1, col2 = st.columns(2)
            nombre = col1.text_input("Nombre del Cliente")
            sistema = col2.selectbox("Seleccione el Sistema", ["Serie 20", "Serie 35", "Eurovent", "Vidrio Templado"])
            
            c_anc, c_alt = st.columns(2)
            ancho = c_anc.number_input("Ancho (mm)", min_value=100, step=10)
            alto = c_alt.number_input("Alto (mm)", min_value=100, step=10)
            
            # Lógica de cálculo (Mantenida)
            precios = {"Serie 20": 1150, "Serie 35": 1450, "Eurovent": 2600, "Vidrio Templado": 3200}
            total = ((ancho * alto) / 1000000) * precios[sistema]
            
            st.markdown(f"<h3 style='color: green;'>Total Estimado: ${total:,.2f} MXN</h3>", unsafe_allow_html=True)
            
            enviar = st.form_submit_button("💾 Guardar y Generar PDF")
            
            if enviar:
                if nombre and total > 0:
                    folio = f"VAZ-{random.randint(1000, 9999)}"
                    datos_finales = {'nombre': nombre, 'sistema': sistema, 'ancho': ancho, 'alto': alto, 'monto': total, 'folio': folio}
                    
                    if guardar_registro(datos_finales):
                        pdf_data = generar_pdf_bytes(datos_finales)
                        st.success(f"✅ Registro guardado con éxito. Folio: {folio}")
                        st.download_button("📥 Descargar Archivo PDF", data=pdf_data, file_name=f"Presupuesto_{folio}.pdf", mime="application/pdf")
                else:
                    st.error("⚠️ Por favor rellena todos los campos.")

    with t2:
        st.subheader("Últimos registros en la nube")
        conn = conectar_db()
        if conn:
            try:
                # Query seguro sin la columna 'estado' para evitar errores previos
                query = """
                    SELECT c.folio_vaz as 'Folio', c.nombre_completo as 'Cliente', 
                           p.importe_neto as 'Monto', p.fecha_emision as 'Fecha'
                    FROM presupuestos p 
                    JOIN clientes c ON p.id_cliente = c.id_cliente 
                    ORDER BY p.id_presupuesto DESC LIMIT 20
                """
                df_ventas = pd.read_sql(query, conn)
                st.dataframe(df_ventas, use_container_width=True, hide_index=True)
            except Exception as e:
                st.warning("No se pudieron cargar los datos del historial.")
            finally:
                conn.close()
