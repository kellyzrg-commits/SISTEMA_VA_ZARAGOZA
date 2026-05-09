import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os
import base64
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Siatema VA Zaragoza",
    page_icon="🏢",
    layout="wide"
)

# Datos fijos del negocio
ASESOR_PRINCIPAL = "Claudio Zaragoza Gorgonio"

# --- FUNCIÓN DE CONEXIÓN SEGURA (Streamlit Secrets) ---
def conectar_db():
    try:
        config = {
            'user': st.secrets.mysql.user,
            'password': st.secrets.mysql.password,
            'host': st.secrets.mysql.host,
            'port': st.secrets.mysql.port,
            'database': st.secrets.mysql.database,
            'ssl_ca': 'ca.pem',
            'ssl_disabled': False
        }
        return mysql.connector.connect(**config)
    except Exception as err:
        st.error(f"Error de conexión: {err}")
        return None

# --- LÓGICA DE ALMACENAMIENTO (Sincronizada con Workbench) ---
def guardar_registro(datos):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # 1. Insertar en la tabla 'clientes' (columnas: folio_vaz, nombre_completo)
        query_cli = "INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)"
        cursor.execute(query_cli, (datos['folio'], datos['nombre']))
        id_cliente = cursor.lastrowid
        
        # 2. Insertar en la tabla 'presupuestos'
        # Columnas reales: id_cliente, ancho, alto, importe_neto, fecha_emision
        query_pre = """
            INSERT INTO presupuestos 
            (id_cliente, ancho, alto, importe_neto, fecha_emision) 
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (
            id_cliente, 
            datos['ancho'], 
            datos['alto'], 
            datos['monto'], 
            datetime.now().date()
        )
        cursor.execute(query_pre, valores)
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
        if os.path.exists("assets/logo_zaragoza.png"):
            self.image("assets/logo_zaragoza.png", 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(24, 46, 82)
        self.cell(80)
        self.cell(110, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'R')
        self.set_font('Arial', '', 9)
        self.cell(190, 5, 'Presupuestos Oficiales | Tehuacán, Puebla', 0, 1, 'R')
        self.ln(20)

def generar_pdf_bytes(datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_fill_color(24, 46, 82)
    pdf.set_text_color(255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(130, 10, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', fill=True)
    pdf.cell(60, 10, f" FOLIO: {datos['folio']}", 1, 1, 'C', fill=True)
    
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
    pdf.cell(30, 12, f"{datos['ancho']} x {datos['alto']} mm", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(60, 12, f"$ {datos['monto']:,.2f} MXN", 1, 1, 'R')
    
    pdf.ln(30)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.set_y(pdf.get_y() + 2)
    pdf.cell(0, 10, ASESOR_PRINCIPAL, 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🏢 Gestión de Presupuestos - VA Zaragoza")

tab1, tab2 = st.tabs(["Nuevo Presupuesto", "Historial"])

with tab1:
    with st.form("form_vaz"):
        nombre = st.text_input("Nombre del Cliente")
        sistema = st.selectbox("Sistema", ["Serie 20 (Nacional)", "Serie 35 (Nacional)", "Línea Eurovent", "Vidrio Templado"])
        c1, c2 = st.columns(2)
        ancho = c1.number_input("Ancho (mm)", min_value=0)
        alto = c2.number_input("Alto (mm)", min_value=0)
        
        # --- LÓGICA DE CÁLCULO AUTOMÁTICO ---
        precios_m2 = {
            "Serie 20 (Nacional)": 1150,
            "Serie 35 (Nacional)": 1450,
            "Línea Eurovent": 2600,
            "Vidrio Templado": 3200
        }
        
        m2 = (ancho * alto) / 1000000
        costo_final = m2 * precios_m2[sistema]
        
        st.subheader(f"Costo Calculado: ${costo_final:,.2f} MXN")
        
        if st.form_submit_button("Generar e Imprimir"):
            if nombre and costo_final > 0:
                folio = f"VAZ-{random.randint(1000, 9999)}"
                datos_p = {
                    'nombre': nombre, 'sistema': sistema, 'ancho': ancho, 
                    'alto': alto, 'monto': costo_final, 'folio': folio
                }
                
                if guardar_registro(datos_p):
                    pdf_bytes = generar_pdf_bytes(datos_p)
                    st.success(f"Guardado. Folio: {folio}")
                    st.download_button("Descargar PDF", data=pdf_bytes, file_name=f"{folio}.pdf")
                    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>', unsafe_allow_html=True)
            else:
                st.error("Por favor llena los campos correctamente.")

with tab2:
    st.subheader("Registros Recientes")
    conn = conectar_db()
    if conn:
        try:
            # Consulta ajustada a las columnas reales de tus tablas
            query = """
                SELECT c.folio_vaz as Folio, c.nombre_completo as Cliente, 
                       p.ancho as Ancho, p.alto as Alto, p.importe_neto as Total, 
                       p.fecha_emision as Fecha
                FROM presupuestos p 
                JOIN clientes c ON p.id_cliente = c.id_cliente 
                ORDER BY p.fecha_emision DESC LIMIT 10
            """
            df = pd.read_sql(query, conn)
            if df.empty:
                st.info("No hay presupuestos registrados aún.")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.warning(f"Error al cargar historial: {e}")
        finally:
            conn.close()
