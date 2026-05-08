import streamlit as st
import mysql.connector

# --- CONFIGURACIÓN DE CONEXIÓN SEGURA ---
def crear_conexion():
    try:
        # Los datos se extraen de Settings > Secrets en Streamlit Cloud
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar con la base de datos en la nube: {e}")
        return None

# --- FUNCIÓN PARA GUARDAR DATOS ---
def guardar_presupuesto(cliente, ancho, alto, total):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = "INSERT INTO presupuestos (cliente, ancho, alto, costo_total) VALUES (%s, %s, %s, %s)"
            valores = (cliente, ancho, alto, total)
            cursor.execute(query, valores)
            conexion.commit()
            st.success(f"✅ Presupuesto de {cliente} guardado en la nube.")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
        finally:
            cursor.close()
            conexion.close()

# --- INTERFAZ DE USUARIO (STREAMLIT) ---
st.set_page_config(page_title="Vidrios y Aluminios Zaragoza", page_icon="🪟")

st.title("🪟 Vidrios y Aluminios Zaragoza")
st.subheader("Cálculo de Presupuestos y Cortes")

# Formulario de entrada
with st.container():
    nombre_cliente = st.text_input("Nombre del Cliente", "Cliente General")
    col1, col2 = st.columns(2)
    
    with col1:
        ancho = st.number_input("Ancho Total (metros)", min_value=0.1, value=0.10, step=0.01)
    with col2:
        alto = st.number_input("Alto Total (metros)", min_value=0.1, value=0.10, step=0.01)

    tipo_ventana = st.selectbox("Tipo de Ventana", ["Corrediza", "Fija", "Proyectable"])

# Lógica de cálculo (Basada en tus correcciones)
if st.button("Calcular Presupuesto y Cortes"):
    # Ejemplo de descuento: (Ancho total - 18) / 2 para zoclos
    descuento_zoclo = (ancho * 100 - 18) / 2 # Convertido a cm para el descuento
    
    # Supongamos un precio base por m2 (puedes ajustarlo)
    precio_m2 = 1200 
    total_calculado = (ancho * alto) * precio_m2
    
    st.write("---")
    st.write(f"### Resultado para {nombre_cliente}:")
    st.metric("Total Estimado", f"${total_calculado:,.2f}")
    st.write(f"📏 **Medida de Zoclos:** {descuento_zoclo:.2f} cm")

    # GUARDAR EN LA NUBE
    guardar_presupuesto(nombre_cliente, ancho, alto, total_calculado)

# --- SECCIÓN DE CONFIGURACIÓN (CON CONTRASEÑA) ---
with st.sidebar:
    st.header("Configuración")
    password = st.text_input("Introduce la contraseña para editar precios", type="password")
    if password == "1234": # Cambia esto por una contraseña real
        st.info("Modo de edición activado")
