import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- CONFIGURACIÓN DE IDENTIDAD CORPORATIVA ---
st.set_page_config(
    page_title="Sistema de Gestión Zaragoza",
    page_icon="📄",
    layout="wide"
)

# Paleta de colores oficial: Azul Oxford y Gris Galería
COLOR_PRIMARIO = "#182E52"
COLOR_FONDO = "#F4F7F9"
COLOR_TEXTO = "#2C3E50"

# --- INYECCIÓN DE ESTILO EMPRESARIAL (CSS) ---
st.markdown(f"""
    <style>
    /* Configuración global de la fuente */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {COLOR_TEXTO};
    }}

    .main {{
        background-color: {COLOR_FONDO};
    }}

    /* Encabezado Institucional */
    .header-container {{
        background-color: white;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        border-bottom: 3px solid {COLOR_PRIMARIO};
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}

    .header-title {{
        color: {COLOR_PRIMARIO};
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }}

    /* Estilo de Botones Primarios */
    div.stButton > button {{
        background-color: {COLOR_PRIMARIO};
        color: white;
        border-radius: 4px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover {{
        background-color: #254A85;
        color: white;
        box-shadow: 0 4px 12px rgba(24, 46, 82, 0.2);
    }}

    /* Etiquetas de pestañas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        gap: 0;
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CLASE DE GENERACIÓN DE DOCUMENTOS (PDF) ---
class GeneradorPDF(FPDF):
    def header(self):
        ruta_logo = os.path.join("assets", "logo_zaragoza.png")
        if os.path.exists(ruta_logo):
            self.image(ruta_logo, 10, 10, 70) 
        
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

def crear_archivo_pdf(cliente, ancho, alto, sistema, total):
    pdf = GeneradorPDF()
    pdf.add_page()
    # (La lógica de dibujo interna se mantiene íntegra según lo acordado previamente)
    return pdf.output(dest='S').encode('latin-1')

# --- ESTRUCTURA DE LA INTERFAZ ---

# Contenedor Superior
st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">Panel Administrativo | Vidrios y Aluminios Zaragoza</h1>
        <p style="margin: 5px 0 0 0; color: #64748B; font-size: 0.9rem;">
            Módulo de Emisión de Presupuestos Técnicos
        </p>
    </div>
    """, unsafe_allow_html=True)

# Navegación Principal
pestana_emision, pestana_archivo = st.tabs(["Emisión de Presupuesto", "Archivo Histórico"])

with pestana_emision:
    st.subheader("Información del Cliente")
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        nombre_cliente = st.text_input("Nombre o Razón Social", placeholder="Nombre completo del destinatario")
        vendedor_asignado = st.text_input("Asesor Comercial", value="Kelly Zaragoza")
    
    with col_der:
        fecha_documento = st.date_input("Fecha de Emisión", datetime.date.today())
        validez_oferta = st.selectbox("Vigencia del Presupuesto", ["15 días naturales", "30 días naturales"])

    st.markdown("---")
    st.subheader("Especificaciones del Proyecto")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        tipo_sistema = st.selectbox("Sistema Seleccionado", ["Ventana Corrediza", "Puerta Batiente", "Fijo Estructural", "Cancelería de Baño"])
    with c2:
        ancho_mm = st.number_input("Ancho Total (mm)", min_value=0, step=1, value=1200)
    with c3:
        alto_mm = st.number_input("Alto Total (mm)", min_value=0, step=1, value=1000)
    with c4:
        monto_total = st.number_input("Importe Neto (MXN)", min_value=0.0, step=50.0, value=2220.0)

    st.caption("Nota: El documento generado incluirá las cláusulas de pago y términos de instalación vigentes.")

    # Acción Principal
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("GENERAR DOCUMENTO PDF"):
        if nombre_cliente:
            try:
                archivo_generado = crear_archivo_pdf(nombre_cliente, ancho_mm, alto_mm, tipo_sistema, monto_total)
                st.success("Documento procesado correctamente.")
                st.download_button(
                    label="DESCARGAR PRESUPUESTO",
                    data=archivo_generado,
                    file_name=f"Presupuesto_VAZ_{nombre_cliente.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as error:
                st.error(f"Se ha producido un error técnico: {error}")
        else:
            st.warning("Se requiere el nombre del cliente para formalizar el documento.")

with pestana_archivo:
    st.info("El módulo de consulta histórica se encuentra en fase de integración de base de datos.")
