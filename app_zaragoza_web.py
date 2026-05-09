import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os
import base64
import random

# --- CONFIGURACIÓN DE IDENTIDAD CORPORATIVA ---
st.set_page_config(
    page_title="Siatema VA Zaragoza | Gestión en la Nube",
    page_icon="🏢",
    layout="wide"
)

# Datos fijos del negocio
ASESOR_PRINCIPAL = "Claudio Zaragoza Gorgonio"
DB_CONFIG = {
    'user': 'avnadmin',
    'password': st.secrets["DB_PASSWORD"],
    'host': 'mysql-2ac11ac4-kellyzrg-4bb6.c.aivencloud.com',
    'port': 10087,
    'database': 'vaz_zaragoza_db', # Actualizado a tu nueva DB
    'ssl_ca': 'ca.pem',
    'ssl_disabled': False
}

# --- FUNCIONES DE BASE DE DATOS ---
def conectar_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        st.error(f"Error de conexión: {err}")
        return None

def guardar_registro(datos):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Registrar Cliente
        query_cli = "INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)"
        cursor.execute(query_cli, (datos['folio'], datos['nombre']))
        id_cliente = cursor.lastrowid
        
        # 2. Registrar Presupuesto
        query_pre = """
            INSERT INTO presupuestos 
            (folio_vaz, id_cliente, nombre_sistema, ancho, alto, importe_neto, vendedor, fecha_emision) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            datos['folio'], id_cliente, datos['sistema'], 
            datos['ancho'], datos['alto'], datos['monto'], 
            ASESOR_PRINCIPAL, datetime.now().date()
        )
        cursor.execute(query_pre, valores)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False
    finally:
        conn.close()

# --- GENERADOR DE PDF PROFESIONAL ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("assets/logo_zaragoza.png"):
            self.image("assets/logo_zaragoza.png", 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(24, 46, 82)
        self.cell(80)
        self.cell(110, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'R')
        self.set_font('Arial', '', 9)
        self.cell(190, 5, 'Tehuacán, Puebla | Presupuestos Oficiales', 0, 1, 'R')
        self.ln(20)

def generar_pdf_bytes(datos):
    pdf = PDF()
    pdf.add_page()
    # Encabezado de Folio
    pdf.set_fill_color(24, 46, 82)
    pdf.set_text_color(255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(130, 10, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', fill=True)
    pdf.cell(60, 10, f" FOLIO: {datos['folio']}", 1, 1, 'C', fill=True)
    
    # Cuerpo
    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 10)
    pdf.cell(130, 8, f" Fecha: {datetime.now().strftime('%d/%m/%Y')}", 1, 0, 'L')
    pdf.cell(60, 8, f" Asesor: {ASESOR_PRINCIPAL}", 1, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(230)
    pdf.cell(100, 8, "SISTEMA / DESCRIPCIÓN", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "MEDIDAS", 1, 0, 'C', fill=True)
    pdf.cell(60, 8, "PRECIO NETO", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 12, datos['sistema'], 1, 0, 'L')
    pdf.cell(30, 12, f"{datos['ancho']}x{datos['alto']}", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(60, 12, f"$ {datos['monto']:,.2f} MXN", 1, 1, 'R')
    
    # Firma
    pdf.ln(30)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.set_y(pdf.get_y() + 2)
    pdf.cell(0, 10, ASESOR_PRINCIPAL, 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🏢 Siatema VA Zaragoza")
tab1, tab2, tab3 = st.tabs(["Presupuestos", "Historial", "Admin"])

with tab1:
    with st.form("nuevo_p"):
        nombre = st.text_input("Nombre del Cliente")
        sistema = st.selectbox("Seleccione el Sistema", ["Serie 20", "Serie 35", "Eurovent", "Templado"])
        c1, c2, c3 = st.columns(3)
        ancho = c1.number_input("Ancho (mm)", value=0)
        alto = c2.number_input("Alto (mm)", value=0)
        monto = c3.number_input("Costo Total Neto", value=0.0)
        
        if st.form_submit_button("Generar y Guardar"):
            if nombre and monto > 0:
                folio = f"VAZ-{random.randint(1000, 9999)}"
                info = {'nombre': nombre, 'sistema': sistema, 'ancho': ancho, 'alto': alto, 'monto': monto, 'folio': folio}
                
                if guardar_registro(info):
                    pdf_data = generar_pdf_bytes(info)
                    st.success(f"Registrado con Folio: {folio}")
                    st.download_button("Descargar PDF Oficial", data=pdf_data, file_name=f"{folio}.pdf")
                    # Visualización
                    base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>', unsafe_allow_html=True)
            else:
                st.warning("Complete todos los campos.")

with tab3:
    st.subheader("Respaldo Mensual (Excel)")
    if st.text_input("Clave Admin", type="password") == "Zaragoza2026":
        if st.button("Generar Excel de este mes"):
            conn = conectar_db()
            df = pd.read_sql("SELECT * FROM presupuestos", conn)
            df.to_excel("respaldo_zaragoza.xlsx", index=False)
            st.download_button("Bajar Archivo", data=open("respaldo_zaragoza.xlsx", "rb"), file_name="Respaldo_VAZ.xlsx")
