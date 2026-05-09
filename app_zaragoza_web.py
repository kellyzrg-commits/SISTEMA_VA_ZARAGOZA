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

# --- FUNCIÓN DE CONEXIÓN ---
def conectar_db():
    try:
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

# --- GUARDAR REGISTRO ---
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
        st.error(f"Error en DB: {e}")
        return False
    finally:
        conn.close()

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
        
        # Precios fijos (como los tenías antes)
        precios = {"Serie 20 (Nacional)": 1150, "Serie 35 (Nacional)": 1450, "Línea Eurovent": 2600, "Vidrio Templado": 3200}
        
        if st.form_submit_button("Generar y Guardar"):
            if nombre and ancho > 0:
                total = ((ancho * alto) / 1000000) * precios[sistema]
                folio = f"VAZ-{random.randint(1000, 9999)}"
                
                datos_p = {'nombre': nombre, 'ancho': ancho, 'alto': alto, 'monto': total, 'folio': folio}
                
                if guardar_registro(datos_p):
                    st.success(f"¡Guardado! Folio: {folio}")
                    st.metric("Total", f"${total:,.2f} MXN")
            else:
                st.error("Rellena todos los campos")

with tab2:
    st.subheader("Registros Recientes")
    conn = conectar_db()
    if conn:
        query = "SELECT c.folio_vaz, c.nombre_completo, p.importe_neto, p.fecha_emision FROM presupuestos p JOIN clientes c ON p.id_cliente = c.id_cliente ORDER BY p.fecha_emision DESC"
        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True)
        conn.close()
