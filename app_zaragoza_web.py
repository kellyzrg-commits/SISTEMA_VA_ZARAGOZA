import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os
import base64
import random

# --- CONFIGURACIÓN DE PÁGINA PROFESIONAL ---
st.set_page_config(
    page_title="Sistema VA Zaragoza | Gestión Profesional",
    page_icon="🏢",
    layout="wide"
)

# Estilos CSS personalizados para mejorar la apariencia
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #182e52; color: white; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DEL NEGOCIO ---
NOMBRE_NEGOCIO = "VIDRIOS Y ALUMINIOS ZARAGOZA"
ASESOR = "Claudio Zaragoza Gorgonio"

# --- CONEXIÓN A BASE DE DATOS ---
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
        st.error(f"Error crítico de conexión: {err}")
        return None

def guardar_registro(datos):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Insertar Cliente
        cursor.execute("INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)", 
                       (datos['folio'], datos['nombre']))
        id_cliente = cursor.lastrowid
        
        # 2. Insertar Presupuesto
        query_pre = "INSERT INTO presupuestos (id_cliente, ancho, alto, importe_neto, fecha_emision) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query_pre, (id_cliente, datos['ancho'], datos['alto'], datos['monto'], datetime.now().date()))
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
        self.set_font('Arial', 'B', 16)
        self.set_text_color(24, 46, 82)
        self.cell(0, 10, NOMBRE_NEGOCIO, 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Tehuacán, Puebla | Calidad y Confianza en Vidrio y Aluminio', 0, 1, 'C')
        self.ln(10)

def generar_pdf_bytes(datos):
    pdf = PDF()
    pdf.add_page()
    # Encabezado de datos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(130, 10, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', fill=True)
    pdf.cell(60, 10, f" FOLIO: {datos['folio']}", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(130, 8, f" Fecha: {datetime.now().strftime('%d/%m/%Y')}", 1, 0, 'L')
    pdf.cell(60, 8, f" Asesor: {ASESOR}", 1, 1, 'C')
    pdf.ln(10)
    
    # Tabla de conceptos
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(24, 46, 82)
    pdf.set_text_color(255)
    pdf.cell(100, 8, "DESCRIPCIÓN DEL SISTEMA", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "MEDIDAS", 1, 0, 'C', fill=True)
    pdf.cell(60, 8, "SUBTOTAL", 1, 1, 'C', fill=True)
    
    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 12, f" Suministro e Instalación de {datos['sistema']}", 1, 0, 'L')
    pdf.cell(30, 12, f" {datos['ancho']}x{datos['alto']} mm", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(60, 12, f" $ {datos['monto']:,.2f} MXN", 1, 1, 'R')
    
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 9)
    pdf.multi_cell(0, 5, "Nota: Este presupuesto tiene una vigencia de 15 días naturales. Los precios pueden variar según ajustes en el costo del material.")
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DE USUARIO ---
st.title(f"🏢 {NOMBRE_NEGOCIO}")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Nuevo Presupuesto", "📋 Historial de Ventas", "⚙️ Configuración"])

with tab1:
    col_form, col_res = st.columns([2, 1])
    
    with col_form:
        st.subheader("Datos del Trabajo")
        with st.container():
            nombre = st.text_input("Nombre Completo del Cliente", placeholder="Ej. Juan Pérez")
            sistema = st.selectbox("Seleccione el Sistema/Material", 
                                 ["Serie 20 (Nacional)", "Serie 35 (Nacional)", "Línea Eurovent", "Vidrio Templado"])
            
            c1, c2 = st.columns(2)
            ancho = c1.number_input("Ancho (mm)", min_value=0, help="Medida horizontal en milímetros")
            alto = c2.number_input("Alto (mm)", min_value=0, help="Medida vertical en milímetros")
            
            precios = {"Serie 20 (Nacional)": 1150, "Serie 35 (Nacional)": 1450, "Línea Eurovent": 2600, "Vidrio Templado": 3200}
            m2 = (ancho * alto) / 1000000
            total_calc = m2 * precios[sistema]

    with col_res:
        st.subheader("Resumen")
        st.metric("Total a Cotizar", f"${total_calc:,.2f} MXN")
        st.write(f"**Material:** {sistema}")
        st.write(f"**Superficie:** {m2:.2f} m²")
        
        btn_guardar = st.button("✅ Generar y Guardar Presupuesto")
        
        if btn_guardar:
            if nombre and ancho > 0 and alto > 0:
                folio = f"VAZ-{random.randint(1000, 9999)}"
                info = {'nombre': nombre, 'sistema': sistema, 'ancho': ancho, 'alto': alto, 'monto': total_calc, 'folio': folio}
                
                if guardar_registro(info):
                    st.success(f"¡Registro exitoso! Folio: {folio}")
                    pdf_bytes = generar_pdf_bytes(info)
                    st.download_button("📥 Descargar PDF Oficial", data=pdf_bytes, file_name=f"{folio}.pdf", mime="application/pdf")
                else:
                    st.error("Error al conectar con la base de datos.")
            else:
                st.warning("Por favor, completa todos los campos obligatorios.")

with tab2:
    st.subheader("Historial Reciente de Presupuestos")
    conn = conectar_db()
    if conn:
        query = """
            SELECT c.folio_vaz as 'Folio', c.nombre_completo as 'Cliente', 
                   p.importe_neto as 'Monto Total', p.fecha_emision as 'Fecha de Emisión'
            FROM presupuestos p 
            JOIN clientes c ON p.id_cliente = c.id_cliente 
            ORDER BY p.fecha_emision DESC
        """
        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True)
        conn.close()

with tab3:
    st.subheader("Configuración del Sistema")
    st.info(f"**Asesor Activo:** {ASESOR}")
    st.write("Versión del Sistema: 2.1 (Relacional)")
    if st.button("Cerrar Sesión"):
        st.cache_data.clear()
        st.rerun()
