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
    page_title="Sistema VA Zaragoza",
    page_icon="🏢",
    layout="wide"
)

# --- FUNCIÓN DE CONEXIÓN ---
def conectar_db():
    try:
        # Asegúrate de tener configurados estos secrets en Streamlit Cloud o tu archivo secrets.toml
        config = {
            'user': st.secrets.mysql.user,
            'password': st.secrets.mysql.password,
            'host': st.secrets.mysql.host,
            'port': st.secrets.mysql.port,
            'database': st.secrets.mysql.database,
            'ssl_ca': 'ca.pem'
        }
        return mysql.connector.connect(**config)
    except Exception as err:
        st.error(f"Error de conexión: {err}")
        return None

# --- OBTENER CATÁLOGO DE SISTEMAS ---
def obtener_sistemas():
    conn = conectar_db()
    sistemas = {}
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_sistema, nombre_sistema, precio_m2 FROM sistemas")
        for (id_s, nombre, precio) in cursor:
            sistemas[nombre] = {'id': id_s, 'precio': float(precio)}
        conn.close()
    return sistemas

# --- GUARDAR REGISTRO (CON RELACIÓN E-R) ---
def guardar_registro(datos):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # 1. Insertar Cliente
        query_cli = "INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)"
        cursor.execute(query_cli, (datos['folio'], datos['nombre']))
        id_cliente = cursor.lastrowid
        
        # 2. Insertar Presupuesto vinculado al Cliente y al Sistema
        query_pre = """
            INSERT INTO presupuestos 
            (id_cliente, id_sistema, ancho, alto, importe_neto, fecha_emision) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (
            id_cliente, 
            datos['id_sistema'], 
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
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Presupuestos y Cotizaciones Profesionales', 0, 1, 'C')
        self.ln(10)

def generar_pdf_bytes(datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Cliente: {datos['nombre']}", 0, 1)
    pdf.cell(0, 10, f"Folio: {datos['folio']}", 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"Sistema: {datos['sistema_nombre']}", 0, 1)
    pdf.cell(0, 10, f"Medidas: {datos['ancho']}mm x {datos['alto']}mm", 0, 1)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Total a Pagar: ${datos['monto']:,.2f} MXN", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DE USUARIO ---
st.title("🏢 Gestión de Presupuestos - VA Zaragoza")

tab1, tab2 = st.tabs(["Nuevo Presupuesto", "Historial de Ventas"])

with tab1:
    sistemas_dict = obtener_sistemas()
    
    with st.form("form_presupuesto"):
        nombre = st.text_input("Nombre del Cliente")
        nombre_sistema = st.selectbox("Selecciona el Sistema/Material", list(sistemas_dict.keys()) if sistemas_dict else ["Cargando..."])
        
        col1, col2 = st.columns(2)
        ancho = col1.number_input("Ancho (mm)", min_value=0)
        alto = col2.number_input("Alto (mm)", min_value=0)
        
        submit = st.form_submit_button("Calcular y Guardar")
        
        if submit:
            if nombre and ancho > 0 and alto > 0:
                # Recuperar datos del sistema desde la DB
                info_s = sistemas_dict[nombre_sistema]
                m2 = (ancho * alto) / 1000000
                total = m2 * info_s['precio']
                folio = f"VAZ-{random.randint(1000, 9999)}"
                
                datos_finales = {
                    'nombre': nombre,
                    'id_sistema': info_s['id'],
                    'sistema_nombre': nombre_sistema,
                    'ancho': ancho,
                    'alto': alto,
                    'monto': total,
                    'folio': folio
                }
                
                if guardar_registro(datos_finales):
                    st.success(f"¡Presupuesto guardado! Folio: {folio}")
                    st.metric("Total Calculado", f"${total:,.2f} MXN")
                    
                    pdf_b = generar_pdf_bytes(datos_finales)
                    st.download_button("Descargar PDF", data=pdf_b, file_name=f"{folio}.pdf")
            else:
                st.warning("Por favor rellena todos los campos.")

with tab2:
    st.subheader("Registros en Base de Datos")
    conn = conectar_db()
    if conn:
        # El JOIN permite ver nombres en lugar de puros IDs
        query = """
            SELECT 
                c.folio_vaz AS Folio, 
                c.nombre_completo AS Cliente, 
                s.nombre_sistema AS Material, 
                p.importe_neto AS Total, 
                p.fecha_emision AS Fecha
            FROM presupuestos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            JOIN sistemas s ON p.id_sistema = s.id_sistema
            ORDER BY p.fecha_emision DESC
        """
        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True)
        conn.close()
