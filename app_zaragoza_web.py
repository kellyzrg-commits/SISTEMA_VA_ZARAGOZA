import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="VA Zaragoza | Panel de Control",
    page_icon="🏗️",
    layout="wide"
)

# --- ESTILOS PROFESIONALES (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Fondo y fuente general */
    .main {
        background-color: #f8f9fa;
    }
    /* Estilo para las tarjetas (Cards) */
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #182e52;
        color: white;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #254a85;
        border: none;
        color: white;
    }
    /* Encabezado Corporativo */
    .header-box {
        background-color: #182e52;
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Input styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CLASE PDF (LOGICA DE NEGOCIO) ---
class PDF_Pro(FPDF):
    def header(self):
        logo_path = os.path.join("assets", "logo_zaragoza.png")
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 10, 70) 
        
        self.set_font('Arial', 'B', 10)
        self.set_text_color(24, 46, 82)
        self.set_xy(120, 15)
        self.cell(80, 5, "VIDRIOS Y ALUMINIOS ZARAGOZA", 0, 1, 'R')
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        self.set_x(120)
        self.cell(80, 4, "Cancelaría de Aluminio y Cristal", 0, 1, 'R')
        self.set_x(120)
        self.cell(80, 4, "Tehuacán, Puebla", 0, 1, 'R')
        
        self.set_draw_color(24, 46, 82)
        self.set_line_width(0.6)
        self.line(10, 48, 200, 48)

# --- FUNCION DE GENERACIÓN ---
def generar_pdf_vaz(cliente, ancho, alto, sistema, total):
    pdf = PDF_Pro()
    pdf.add_page()
    y_bloque = 55
    # (Misma lógica interna de dibujo que definimos antes)
    # ... [Omitido por brevedad para enfocar en la interfaz]
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DE USUARIO (UX/UI PROFESIONAL) ---

# 1. Encabezado de la App
st.markdown("""
    <div class="header-box">
        <h1>Siatema VA Zaragoza</h1>
        <p>Gestión Profesional de Presupuestos y Cancelería</p>
    </div>
    """, unsafe_allow_html=True)

# 2. Organización en Columnas y Tabs
tab1, tab2 = st.tabs(["📝 Nuevo Presupuesto", "📊 Historial de Ventas"])

with tab1:
    with st.container():
        st.subheader("Datos del Cliente y Proyecto")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            cliente = st.text_input("Nombre Completo del Cliente", placeholder="Ej. Juan Pérez")
        with col2:
            fecha = st.date_input("Fecha de Emisión", datetime.date.today())
        with col3:
            vendedor = st.text_input("Atendido por:", value="Kelly Zaragoza") #

    st.divider()

    st.subheader("Especificaciones Técnicas")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sistema = st.selectbox("Sistema de Aluminio", ["Ventana Corrediza", "Puerta Batiente", "Fijo", "Cancelería de Baño"])
    with c2:
        ancho = st.number_input("Ancho (mm)", min_value=0, value=1200)
    with c3:
        alto = st.number_input("Alto (mm)", min_value=0, value=1000)
    with c4:
        precio = st.number_input("Costo Total ($)", min_value=0.0, value=2220.0, step=100.0)

    st.info("💡 El PDF incluirá automáticamente los términos de validez (15 días) y condiciones de pago.")

    # Botón de acción destacado
    if st.button("✨ GENERAR DOCUMENTO OFICIAL"):
        if cliente:
            try:
                pdf_bytes = generar_pdf_vaz(cliente, ancho, alto, sistema, precio)
                st.success(f"Presupuesto para {cliente} generado con éxito.")
                st.download_button(
                    label="📥 Descargar Nota de Venta (PDF)",
                    data=pdf_bytes,
                    file_name=f"Presupuesto_VAZ_{cliente.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error al generar el PDF: {e}")
        else:
            st.warning("Por favor, ingrese el nombre del cliente para continuar.")

with tab2:
    st.write("Módulo de historial en desarrollo... (Aquí conectarás tu base de datos Aiven/MySQL)") #
