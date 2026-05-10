import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VAZ-Control V3.1", layout="wide")

# Estilos personalizados para mejorar la interfaz
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    .css-1r6slb0 { background-color: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    </style>
""", unsafe_allow_html=True)

# --- 1. FUNCIONES DE BASE DE DATOS ---
def conectar_db():
    try:
        # Asegúrate de que estos nombres coincidan con tus st.secrets
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
    except Exception as e:
        st.error(f"Error crítico de conexión: {e}")
        return None

def validar_usuario(usuario, password):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id_usuario, rol, nombre_real FROM usuarios WHERE nombre_usuario = %s AND password_hash = %s"
        cursor.execute(query, (usuario, password))
        res = cursor.fetchone()
        conn.close()
        return res
    return None

def obtener_precios_db():
    conn = conectar_db()
    if conn:
        df = pd.read_sql("SELECT id_config, concepto, costo_base_m2 FROM configuracion_precios", conn)
        conn.close()
        return df
    return pd.DataFrame()

def guardar_cotizacion_completa(datos):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Insertar Cliente
        query_cli = "INSERT INTO clientes (folio_vaz, nombre_completo, telefono, direccion) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_cli, (datos['folio'], datos['nombre'], datos['tel'], datos['dir']))
        id_cliente = cursor.lastrowid
        
        # 2. Insertar Presupuesto con campos técnicos
        query_pre = """
            INSERT INTO presupuestos 
            (id_cliente, id_usuario, serie, modelo, color, espesor, ancho_mm, alto_mm, monto_total, fecha_emision) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            id_cliente, st.session_state.uid, datos['serie'], datos['modelo'],
            datos['color'], datos['espesor'], datos['ancho'], datos['alto'],
            datos['total'], datetime.now()
        )
        cursor.execute(query_pre, valores)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al guardar en DB: {e}")
        return False

# --- 2. SISTEMA DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏢 Vidrios y Aluminios Zaragoza")
    st.subheader("VAZ-Control V3.1 | Acceso Profesional")
    
    with st.container():
        col_l, col_r = st.columns([1, 1])
        with col_l:
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("Entrar al Sistema"):
                user = validar_usuario(u, p)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.rol = user['rol']
                    st.session_state.nombre = user['nombre_real']
                    st.session_state.uid = user['id_usuario']
                    st.rerun()
                else:
                    st.error("Acceso denegado. Verifica tus datos.")

# --- 3. PANEL PRINCIPAL ---
else:
    st.sidebar.title("VAZ-Control")
    st.sidebar.info(f"Usuario: {st.session_state.nombre}\nRol: {st.session_state.rol.upper()}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

    # --- VISTA ADMINISTRADOR ---
    if st.session_state.rol == 'administrador':
        st.header("⚙️ Gestión de Costos y Márgenes")
        df_p = obtener_precios_db()
        
        if not df_p.empty:
            edited_df = st.data_editor(
                df_p, 
                column_config={"costo_base_m2": st.column_config.NumberColumn("Costo Base ($)", format="$ %.2f")},
                disabled=["id_config", "concepto"],
                hide_index=True
            )
            if st.button("Guardar Cambios en Precios"):
                conn = conectar_db()
                if conn:
                    cursor = conn.cursor()
                    for i, row in edited_df.iterrows():
                        cursor.execute("UPDATE configuracion_precios SET costo_base_m2 = %s WHERE id_config = %s", 
                                     (row['costo_base_m2'], row['id_config']))
                    conn.commit()
                    conn.close()
                    st.success("Precios actualizados correctamente.")

    # --- VISTA ASESOR ---
    else:
        st.header("📝 Nueva Cotización Técnica")
        
        with st.form("form_cotizacion"):
            st.subheader("1. Información del Cliente")
            c_nom, c_tel = st.columns([2, 1])
            nombre = c_nom.text_input("Nombre del Cliente")
            tel = c_tel.text_input("Teléfono")
            direccion = st.text_input("Dirección de la Obra")
            
            st.divider()
            st.subheader("2. Especificaciones de la Estructura")
            
            df_precios = obtener_precios_db()
            f1, f2, f3 = st.columns(3)
            serie = f1.selectbox("Serie / Línea", df_precios['concepto'].tolist())
            modelo = f2.selectbox("Modelo", ["Fijo", "Corrediza", "Batiente", "Proyectante", "Duovent"])
            color = f3.selectbox("Color", ["Blanco", "Negro", "Natural", "Bronce", "Madera"])
            
            f4, f5, f6 = st.columns(3)
            ancho = f4.number_input("Ancho (mm)", min_value=1)
            alto = f5.number_input("Alto (mm)", min_value=1)
            espesor = f6.selectbox("Espesor Cristal", ["3mm", "6mm", "9mm", "10mm (Templado)", "12mm"])
            
            st.divider()
            
            # Cálculo de Ingeniería
            costo_base = float(df_precios[df_precios['concepto'] == serie]['costo_base_m2'].values[0])
            area_m2 = (ancho * alto) / 1000000
            total_calc = (area_m2 * costo_base) * 1.50 # Incluye 50% mano de obra
            
            st.write(f"## Total: ${total_calc:,.2f} MXN")
            
            if st.form_submit_button("💾 Guardar y Generar Presupuesto"):
                if nombre and ancho > 0:
                    folio = f"VAZ-{random.randint(1000, 9999)}"
                    datos_finales = {
                        'folio': folio, 'nombre': nombre, 'tel': tel, 'dir': direccion,
                        'serie': serie, 'modelo': modelo, 'color': color, 'espesor': espesor,
                        'ancho': ancho, 'alto': alto, 'total': total_calc
                    }
                    if guardar_cotizacion_completa(datos_finales):
                        st.success(f"Cotización Guardada. Folio: {folio}")
                        st.balloons()
                else:
                    st.error("Datos incompletos.")
