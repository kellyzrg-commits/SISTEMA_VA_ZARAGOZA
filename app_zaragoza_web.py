import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os
import base64
import random

# --- 1. SISTEMA DE SEGURIDAD (Login) ---
def check_password():
    def password_guessed():
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Acceso al Sistema - VA Zaragoza", type="password", on_change=password_guessed, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Acceso al Sistema - VA Zaragoza", type="password", on_change=password_guessed, key="password")
        st.error("😕 Contraseña incorrecta")
        return False
    else:
        return True

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Siatema VA Zaragoza", page_icon="🏢", layout="wide")

if check_password():
    # Datos fijos
    ASESOR_PRINCIPAL = "Claudio Zaragoza Gorgonio"

    # --- CONEXIÓN A BASE DE DATOS (Aiven) ---
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

    # --- GUARDAR EN DB ---
    def guardar_registro(datos):
        conn = conectar_db()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # Insertar cliente
            cursor.execute("INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)", (datos['folio'], datos['nombre']))
            id_cliente = cursor.lastrowid
            
            # Insertar presupuesto (Sin la columna 'estado' para evitar errores)
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

    # --- GENERADOR DE PDF ---
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.set_text_color(24, 46, 82)
            self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
            self.set_font('Arial', '', 9)
            self.cell(0, 5, 'Presupuestos Oficiales | Tehuacán, Puebla', 0, 1, 'C')
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
        pdf.cell(100, 8, "SISTEMA / DESCRIPCIÓN", 1, 0, 'C', fill=True)
        pdf.cell(30, 8, "MEDIDAS", 1, 0, 'C', fill=True)
        pdf.cell(60, 8, "PRECIO NETO", 1, 1, 'C', fill=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(100, 12, datos['sistema'], 1, 0, 'L')
        pdf.cell(30, 12, f"{datos['ancho']}x{datos['alto']} mm", 1, 0, 'C')
        pdf.cell(60, 12, f"$ {datos['monto']:,.2f}", 1, 1, 'R')
        return pdf.output(dest='S').encode('latin-1')

    # --- INTERFAZ ---
    st.title("🏢 Gestión VA Zaragoza")
    t1, t2 = st.tabs(["Nuevo Presupuesto", "Historial"])

    with t1:
        with st.form("form_vaz"):
            nombre = st.text_input("Nombre del Cliente")
            sistema = st.selectbox("Sistema", ["Serie 20", "Serie 35", "Eurovent", "Templado"])
            c1, c2 = st.columns(2)
            ancho = c1.number_input("Ancho (mm)", min_value=0)
            alto = c2.number_input("Alto (mm)", min_value=0)
            
            precios = {"Serie 20": 1150, "Serie 35": 1450, "Eurovent": 2600, "Templado": 3200}
            m2 = (ancho * alto) / 1000000
            total = m2 * precios[sistema]
            st.subheader(f"Total: ${total:,.2f} MXN")
            
            if st.form_submit_button("Guardar e Imprimir"):
                if nombre and total > 0:
                    folio = f"VAZ-{random.randint(1000, 9999)}"
                    datos = {'nombre': nombre, 'sistema': sistema, 'ancho': ancho, 'alto': alto, 'monto': total, 'folio': folio}
                    if guardar_registro(datos):
                        pdf_bytes = generar_pdf_bytes(datos)
                        st.success(f"Guardado. Folio: {folio}")
                        st.download_button("Descargar PDF", data=pdf_bytes, file_name=f"{folio}.pdf")
                else: st.error("Datos incompletos.")

    with t2:
        st.subheader("Registros Recientes")
        conn = conectar_db()
        if conn:
            try:
                query = """
                    SELECT c.folio_vaz as Folio, c.nombre_completo as Cliente, 
                           p.importe_neto as Total, p.fecha_emision as Fecha
                    FROM presupuestos p 
                    JOIN clientes c ON p.id_cliente = c.id_cliente 
                    ORDER BY p.id_presupuesto DESC LIMIT 15
                """
                df = pd.read_sql(query, conn)
                st.dataframe(df, use_container_width=True, hide_index=True)
            finally: conn.close()
