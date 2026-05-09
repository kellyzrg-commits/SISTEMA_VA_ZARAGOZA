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
        
        # 1. POSICIÓN DEL LOGO (Movido a donde marca la flecha)
        if os.path.exists(logo_path):
            # X=70 lo centra más hacia donde apunta tu flecha
            # Y=10 lo mantiene en la parte superior
            self.image(logo_path, 70, 10, 60) 
        
        # 2. TEXTO DE CABECERA (Extremo Derecho)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*AZUL_ZARAGOZA)
        self.set_xy(120, 12)
        self.cell(80, 5, "VIDRIOS Y ALUMINIOS ZARAGOZA", 0, 1, 'R')
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        self.set_x(120)
        self.cell(80, 4, "Cancelaría de Aluminio y Cristal", 0, 1, 'R')
        self.set_x(120)
        self.cell(80, 4, "Tehuacán, Puebla", 0, 1, 'R')
        
        # 3. LÍNEA DE SEPARACIÓN
        # La mantenemos en Y=48 para que sirva de base al logo centrado
        self.set_draw_color(*AZUL_ZARAGOZA)
        self.set_line_width(0.5)
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
    
    # --- COORDENADA DE INICIO ---
    # Bajamos a Y=55 para que los cuadros no toquen la línea azul
    y_bloque = 55
    
    # Datos Presupuesto
    pdf.draw_box(10, y_bloque, 90, 25, "DATOS DEL PRESUPUESTO")
    pdf.set_font('Arial', '', 9)
    pdf.set_xy(12, y_bloque + 8)
    pdf.cell(80, 5, f"FECHA: {datetime.date.today()}", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "VALIDEZ: 15 Días naturales", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "PAGO: 50% Anticipo / 50% Finalizar", 0, 1)

    # Datos Cliente
    pdf.draw_box(105, y_bloque, 95, 25, "DATOS DEL CLIENTE")
    pdf.set_xy(107, y_bloque + 8)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 5, f"CLIENTE: {cliente.upper()}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(107)
    pdf.cell(90, 5, "Atención: Personalizada", 0, 1)
    pdf.set_x(107)
    pdf.cell(90, 5, "Incluye: Suministro e Instalación", 0, 1)

    # Diseño y Descripción (Y=90)
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
    pdf.multi_cell(90, 5, f"* Aluminio de primera calidad\n* Vidrio claro de 6mm\n* Sellado profesional\n* Herrajes de alta resistencia.")

    # Tabla Total (Y=160)
    y_total = 160
    pdf.set_xy(10, y_total)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(130, 10, "  CONCEPTO GENERAL", 1, 0, 'L', fill=True)
    pdf.cell(60, 10, "TOTAL", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(130, 15, f"  Fabricación e Instalación de {sistema}", 1)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 15, f"$ {total:,.2f} MXN", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("📂 Generador de Presupuestos - VA Zaragoza")

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Cliente", "Kelly Zaragoza")
    producto = st.selectbox("Producto", ["Ventana Corrediza", "Ventana Fija", "Puerta Batiente"])
with col2:
    ancho_val = st.number_input("Ancho (mm)", 1200)
    alto_val = st.number_input("Alto (mm)", 1000)
    precio = st.number_input("Precio Final", 2220.0)

if st.button("🚀 Crear PDF con Logo Centrado"):
    pdf_final = generar_pdf_vaz(nombre, ancho_val, alto_val, producto, precio)
    st.download_button(
        label="⬇️ Descargar Nota de Venta",
        data=pdf_final,
        file_name=f"VAZ_{nombre}.pdf",
        mime="application/pdf"
    )
