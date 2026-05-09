import streamlit as st
from fpdf import FPDF
import datetime
import os
import base64

# --- CONFIGURACIÓN DE IDENTIDAD CORPORATIVA ---
st.set_page_config(
    page_title="Sistema de Gestión Integral | VA Zaragoza",
    page_icon="🏢",
    layout="wide"
)

# Constantes Estéticas
COLOR_PRIMARIO = "#182E52"
COLOR_SECUNDARIO = "#64748B"
COLOR_FONDO = "#F4F7F9"

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- ESTILOS CSS PROFESIONALES ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .main {{
        background-color: {COLOR_FONDO};
    }}

    /* Encabezado Principal */
    .header-container {{
        background-color: white;
        padding: 1.5rem 2.5rem;
        border-radius: 12px;
        border-bottom: 4px solid {COLOR_PRIMARIO};
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }}

    .logo-img {{
        max-height: 70px;
        width: auto;
    }}

    .header-title {{
        color: {COLOR_PRIMARIO};
        font-weight: 700;
        margin: 0;
        font-size: 1.6rem;
    }}

    /* Estilización de Tarjetas de Métricas */
    .metric-card {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid {COLOR_PRIMARIO};
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}

    /* Botones de Acción */
    div.stButton > button {{
        background-color: {COLOR_PRIMARIO};
        color: white;
        font-weight: 600;
        border-radius: 4px;
        border: none;
        width: 100%;
        height: 3rem;
        transition: 0.3s;
    }}

    div.stButton > button:hover {{
        background-color: #254A85;
        box-shadow: 0 4px 12px rgba(24, 46, 82, 0.15);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- RENDERIZADO DEL ENCABEZADO ---
ruta_logo = os.path.join("assets", "logo_zaragoza.png")
if os.path.exists(ruta_logo):
    logo_b64 = get_base64_of_bin_file(ruta_logo)
    st.markdown(f"""
        <div class="header-container">
            <img src="data:image/png;base64,{logo_b64}" class="logo-img">
            <div>
                <h1 class="header-title">Panel de Control Empresarial</h1>
                <p style="margin:0; color:{COLOR_SECUNDARIO};">Vidrios y Aluminios Zaragoza | Gestión de Proyectos</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN POR MÓDULOS ---
tabs = st.tabs([
    "📊 Tablero", 
    "📝 Presupuestos", 
    "🏗️ Seguimiento de Obra", 
    "📦 Inventarios", 
    "👥 Clientes", 
    "⚙️ Configuración"
])

# --- 1. TABLERO (ANÁLISIS DE DATOS) ---
with tabs[0]:
    st.subheader("Resumen Operativo")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="metric-card"><small>Ventas del Mes</small><h3>$45,200.00</h3></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-card"><small>Proyectos Activos</small><h3>12</h3></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-card"><small>Cotizaciones Pendientes</small><h3>8</h3></div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="metric-card"><small>Eficiencia de Instalación</small><h3>94%</h3></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Nota: Los datos financieros se actualizan automáticamente tras cada cierre de venta registrado.")

# --- 2. EMISIÓN DE PRESUPUESTOS ---
with tabs[1]:
    st.subheader("Nueva Cotización Técnica")
    with st.expander("Información General", expanded=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Razón Social del Cliente")
        asesor = c2.text_input("Asesor Responsable", value="Kelly Zaragoza")
    
    with st.expander("Especificaciones de Cancelería", expanded=True):
        s1, s2, s3, s4 = st.columns(4)
        sistema = s1.selectbox("Línea de Aluminio", ["Nacional 2\"", "Nacional 3\"", "Eurovent", "Templado"])
        ancho = s2.number_input("Ancho (mm)", value=1000)
        alto = s3.number_input("Alto (mm)", value=1000)
        total = s4.number_input("Precio Final (MXN)", value=0.0)

    if st.button("GENERAR Y REGISTRAR PRESUPUESTO"):
        st.success("Documento generado. El archivo se ha vinculado al historial del cliente.")

# --- 3. SEGUIMIENTO DE OBRA ---
with tabs[2]:
    st.subheader("Control de Proyectos en Ejecución")
    # Simulación de tabla de proyectos
    st.table({
        "Proyecto ID": ["VA-001", "VA-002", "VA-003"],
        "Cliente": ["Residencial Tehuacán", "Local Centro", "Oficinas Norte"],
        "Estatus": ["En Fabricación", "Pintura", "Instalación Programada"],
        "Fecha Entrega": ["2026-05-15", "2026-05-18", "2026-05-20"]
    })

# --- 4. INVENTARIOS ---
with tabs[3]:
    st.subheader("Control de Stock de Materiales")
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        st.write("**Perfiles de Aluminio (Tramos)**")
        st.progress(0.75, text="Bolsa Blanca 3\" (75%)")
        st.progress(0.30, text="Anodizado Natural (30%) - Reabastecer pronto")
    with col_inv2:
        st.write("**Herrajes y Accesorios**")
        st.write("- Carretillas D-200: 45 pzs")
        st.write("- Sellador de Silicón (Cartuchos): 12 pzs")

# --- 5. GESTIÓN DE CLIENTES (CRM) ---
with tabs[4]:
    st.subheader("Directorio de Clientes")
    st.text_input("🔍 Buscar cliente por nombre o folio...")
    st.button("AÑADIR NUEVO CLIENTE")

# --- 6. CONFIGURACIÓN ---
with tabs[5]:
    st.subheader("Parámetros del Sistema")
    st.checkbox("Habilitar impuestos automáticos (IVA 16%)", value=True)
    st.text_input("Ubicación de Respaldo de Base de Datos", value="Cloud Server / Aiven")
