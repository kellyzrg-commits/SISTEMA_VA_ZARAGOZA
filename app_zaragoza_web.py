import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE ESTILO ---
st.set_page_config(page_title="VAZ-Control V3.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .admin-card { background-color: #e6fffa; padding: 20px; border-radius: 10px; border: 1px solid #38b2ac; }
    .asesor-card { background-color: #ebf8ff; padding: 20px; border-radius: 10px; border: 1px solid #4299e1; }
    </style>
""", unsafe_allow_html=True)

# --- 1. FUNCIONES DE BASE DE DATOS ---
def conectar_db():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
    except Exception as e:
        st.error(f"Error de conexión: {e}")
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

def actualizar_precio_db(id_c, nuevo_precio):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE configuracion_precios SET costo_base_m2 = %s WHERE id_config = %s", (nuevo_precio, id_c))
        conn.commit()
        conn.close()
        return True
    return False

# --- 2. SISTEMA DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏢 Vidrios y Aluminios Zaragoza - V3.0")
    with st.container(border=True):
        st.subheader("Acceso al Sistema")
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            user = validar_usuario(u, p)
            if user:
                st.session_state.logged_in = True
                st.session_state.rol = user['rol']
                st.session_state.nombre = user['nombre_real']
                st.session_state.uid = user['id_usuario']
                st.rerun()
            else:
                st.error("Credenciales inválidas")

# --- 3. INTERFAZ PRINCIPAL (LOGUEADO) ---
else:
    st.sidebar.title("VAZ-Control")
    st.sidebar.write(f"Sesión: **{st.session_state.nombre}**")
    st.sidebar.write(f"Rol: {st.session_state.rol.capitalize()}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

    # --- MODO ADMINISTRADOR ---
    if st.session_state.rol == 'administrador':
        st.header("⚙️ Panel de Gestión de Precios (Admin)")
        st.info("Modifica los costos base por m2. Estos cambios afectan a todas las cotizaciones futuras.")
        
        precios_df = obtener_precios_db()
        if not precios_df.empty:
            for index, row in precios_df.iterrows():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    col1.write(f"**{row['concepto']}**")
                    nuevo_p = col2.number_input(f"Costo m2", value=float(row['costo_base_m2']), key=f"p_{row['id_config']}")
                    if col3.button("Actualizar", key=f"btn_{row['id_config']}"):
                        if actualizar_precio_db(row['id_config'], nuevo_p):
                            st.toast(f"Actualizado: {row['concepto']}")
        
        st.divider()
        st.subheader("📊 Reporte de Ventas Globales")
        # Aquí podrías cargar un df con todos los presupuestos de la DB

    # --- MODO ASESOR ---
    else:
        st.header("📝 Cotizador Técnico (Asesor)")
        
        col_form, col_visual = st.columns([1, 1])
        
        with col_form:
            with st.container(border=True):
                st.write("### Datos de la Obra")
                cliente = st.text_input("Nombre del Cliente")
                
                # Traer precios actualizados de la DB
                df_p = obtener_precios_db()
                opciones = df_p['concepto'].tolist()
                seleccion = st.selectbox("Material / Línea", opciones)
                
                c1, c2 = st.columns(2)
                ancho = c1.number_input("Ancho (mm)", min_value=100, step=1)
                alto = c2.number_input("Alto (mm)", min_value=100, step=1)
                
                # Lógica de Cálculo
                costo_base = df_p[df_p['concepto'] == seleccion]['costo_base_m2'].values[0]
                m2 = (ancho * alto) / 1000000
                subtotal = m2 * float(costo_base)
                total = subtotal * 1.50 # +50% Mano de obra
                
                st.markdown(f"### Total: ${total:,.2f} MXN")
                st.caption(f"Incluye material y 50% de mano de obra. (Precio base: ${costo_base}/m2)")

        with col_visual:
            st.write("### Visualización de Estructura")
            # Dibujo proporcional simple
            ratio = ancho / alto if alto != 0 else 1
            st.markdown(f"""
                <div style="width:100%; height:300px; display:flex; justify-content:center; align-items:center; background:#f0f2f6; border-radius:10px;">
                    <div style="width:{200*ratio if ratio < 1.5 else 250}px; height:200px; border:5px solid #2c3e50; background:rgba(52,152,219,0.2); display:flex; justify-content:center; align-items:center;">
                        <b>{ancho}x{alto}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("💾 Guardar y Generar Folio"):
                if cliente:
                    folio = f"VAZ-{random.randint(1000, 9999)}"
                    # Aquí llamarías a la función para insertar en 'clientes' y 'presupuestos'
                    st.success(f"Presupuesto guardado con éxito. Folio: {folio}")
                    st.balloons()
                else:
                    st.warning("Por favor ingresa el nombre del cliente.")
