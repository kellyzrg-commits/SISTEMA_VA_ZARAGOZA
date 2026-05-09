import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema VA Zaragoza", layout="wide")

# Color Institucional
AZUL_ZARAGOZA = (24, 46, 82)

class PDF_Pro(FPDF):
    def header(self):
        logo_path = os.path.join("assets", "logo_zaragoza.png")
        
        # 1. POSICIÓN DEL LOGO (Arriba de la línea)
        if os.path.exists(logo_path):
            # X=10, Y=10 para que esté en la esquina superior izquierda
            # El tamaño de 70 es ideal para que luzca profesional
            self.image(logo_path, 10, 10, 70) 
        
        # 2. TEXTO DE CABECERA (Alineado a la derecha del logo)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*AZUL_ZARAGOZA)
        self.set_xy(120, 15)
        self.cell(80, 5, "VIDRIOS Y ALUMINIOS ZARAGOZA", 0, 1, 'R')
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        self.set_x(120)
        self.cell(80, 4, "Cancelaría de Aluminio y Cristal", 0, 1, 'R')
        self.set_x(120)
        self.cell(80, 4, "Tehuacán, Puebla", 0, 1, 'R')
        
        # 3. LÍNEA AZUL (Actúa como separador debajo del logo)
        # La colocamos en Y=48 para que el logo (que mide unos 35-40mm de alto) 
        # quede totalmente por encima.
        self.set_draw_color(*AZUL_ZARAGOZA)
        self.set_line_width(0.6)
        self.line(10, 48, 200, 48)

    def draw_box(self, x, y, w, h, title):
        self.set_fill_color(*AZUL_ZARAGOZA)
        self.set_text_color(255, 255, 255)
        self.set_xy(x, y)
        self.set_font('Arial', 'B', 9)
        self.cell(w, 6, f"  {title}", 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        self.rect(x, y, w, h)

def generar_pdf_vaz(cliente, ancho, alto, sistema, total):
    pdf = PDF_Pro()
    pdf.add_page()
    
    # --- COORDENADA DE INICIO DE CONTENIDO ---
    # Bajamos el inicio a Y=55 para que los cuadros no toquen la línea azul
    y_bloque = 55
    
    # Bloque Datos Presupuesto
    pdf.draw_box(10, y_bloque, 90, 25, "DATOS DEL PRESUPUESTO")
    pdf.set_font('Arial', '', 9)
    pdf.set_xy(12, y_bloque + 8)
    pdf.cell(80, 5, f"FECHA: {datetime.date.today()}", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "VALIDEZ: 15 Días naturales", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "PAGO: 50% Anticipo / 50% Finalizar", 0, 1)

    # Bloque Datos Cliente
    pdf.draw_box(105, y_bloque, 95, 25, "DATOS DEL CLIENTE")
    pdf.set_xy(107, y_bloque + 8)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 5, f"CLIENTE: {cliente.upper()}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(107)
    pdf.cell(90, 5, "Servicio: Fabricación e Instalación", 0, 1)
    pdf.set_x(107)
    pdf.cell(90, 5, "Incluye: Suministro y Colocación", 0, 1)

    # Bloque Diseño (Y=90)
    y_tec = 90
    pdf.set_fill_color(*AZUL_ZARAGOZA)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y_tec)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 7, "  DISEÑO ESTIMADO", 1, 0, 'L', fill=True)
    pdf.cell(95, 7, "  DESCRIPCIÓN", 1, 1, 'L', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.rect(10, y_tec + 7, 90, 55) 
    pdf.set_xy(15, y_tec + 25)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(80, 5, f"Sistema: {sistema}", 0, 1, 'C')
    pdf.set_x(15)
    pdf.cell(80, 5, f"{ancho} x {alto} mm", 0, 1, 'C')

    pdf.set_xy(105, y_tec + 10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 6, f"{sistema}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(105)
    pdf.multi_cell(90, 5, f"* Aluminio de alta calidad\n* Vidrio claro 6mm\n* Sellado profesional\n* Herrajes de alta resistencia.")

    # Tabla Total (Y=160)
    y_total = 160
    pdf.set_xy(10, y_total)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(130, 10, "  CONCEPTO", 1, 0, 'L', fill=True)
    pdf.cell(60, 10, "TOTAL", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(130, 15, f"  Fabricación e Instalación de {sistema}", 1)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 15, f"$ {total:,.2f} MXN", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ STREAMLIT ---
st.title("🗒️ Sistema de Notas VAZ")

col1, col2 = st.columns(2)
with col1:
    c = st.text_input("Nombre del Cliente", "Kelly Zaragoza")
    s = st.selectbox("Tipo de Sistema", ["Ventana Corrediza", "Puerta Batiente", "Fijo", "Cancelería"])
with col2:
    w = st.number_input("Ancho (mm)", 1200)
    h = st.number_input("Alto (mm)", 1000)
    p = st.number_input("Costo Total ($)", 2220.0)

if st.button("🏗️ Generar Documento PDF"):
    pdf_bytes = generar_pdf_vaz(c, w, h, s, p)
    st.download_button(
        label="⬇️ Descargar PDF",
        data=pdf_bytes,
        file_name=f"Nota_VAZ_{c}.pdf",
        mime="application/pdf"
    )
