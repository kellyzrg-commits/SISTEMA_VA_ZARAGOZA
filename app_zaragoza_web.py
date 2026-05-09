import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os
import base64
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Siatema VA Zaragoza", layout="wide")

# Función para conectar usando los Secrets de Streamlit
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

# Función para guardar registros en las dos tablas
def guardar_registro(datos):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # 1. Insertar en 'clientes'
        query_cli = "INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)"
        cursor.execute(query_cli, (datos['folio'], datos['nombre']))
        id_cliente = cursor.lastrowid # Obtenemos el ID generado automáticamente
        
        # 2. Insertar en 'presupuestos' (Ajustado a tus columnas de Workbench)
        query_pre = """
            INSERT INTO presupuestos 
            (id_cliente, id_sistema, ancho, alto, importe_neto, fecha_emision) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        # Usamos 1 como id_sistema por defecto para este ejemplo
        valores = (id_cliente, 1, datos['ancho'], datos['alto'], datos['monto'], datetime.now().date())
        cursor.execute(query_pre, valores)
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False
    finally:
        conn.close()

# --- INTERFAZ DE USUARIO ---
st.title("🏢 Gestión de Presupuestos - VA Zaragoza")

with st.form("form_presupuesto"):
    nombre = st.text_input("Nombre del Cliente")
    col1, col2 = st.columns(2)
    ancho = col1.number_input("Ancho (mm)", min_value=0)
    alto = col2.number_input("Alto (mm)", min_value=0)
    
    if st.form_submit_button("Guardar Presupuesto"):
        if nombre and ancho > 0 and alto > 0:
            # Cálculo rápido: $1,500 por metro cuadrado
            monto = (ancho * alto / 1,000,000) * 1500
            folio = f"VAZ-{random.randint(1000, 9999)}"
            
            if guardar_registro({'nombre': nombre, 'ancho': ancho, 'alto': alto, 'monto': monto, 'folio': folio}):
                st.success(f"¡Presupuesto guardado con éxito! Folio: {folio}")
        else:
            st.warning("Por favor completa todos los campos.")

# --- SECCIÓN DE HISTORIAL ---
st.subheader("Registros Recientes")
conn = conectar_db()
if conn:
    query = """
        SELECT c.folio_vaz as Folio, c.nombre_completo as Cliente, 
               p.importe_neto as Total, p.fecha_emision as Fecha
        FROM presupuestos p 
        JOIN clientes c ON p.id_cliente = c.id_cliente 
        ORDER BY p.fecha_emision DESC LIMIT 5
    """
    df = pd.read_sql(query, conn)
    st.table(df)
    conn.close()
