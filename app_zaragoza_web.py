import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Presupuestos Pro", layout="wide")

# Color del Logo (Azul Marino Zaragoza)
AZUL_ZARAGOZA = (24, 46, 82) 

class PDF_Pro(FPDF):
    def header(self):
        # Ruta del logo
        logo_path = os.path.join("assets", "logo_zaragoza.png")
        
        if os.path.exists(logo_path):
            # Aumentamos a 60 para que sea muy legible, pero lo mantenemos en la esquina
            self.image(logo_path, 10, 10, 60) 
        else:
            self.set_font('Arial', 'B', 15)
            self.set_text_color(*AZUL_ZARAGOZA)
            self.cell(60, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA')
        
        # Información de la Empresa (Derecha)
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
        
        # LÍNEA DIVISORIA: La bajamos a 45 para que el logo respire
        self.set_draw_color(*AZUL_ZARAGOZA)
        self.set_line_width(0.6)
        self.line(10, 45, 200, 45)

    def draw_box(self, x, y, w, h, title):
        self.set_fill_color(*AZUL_ZARAGOZA)
        self.set_text_color(255, 255, 255)
        self.set_xy(x, y)
        self.set_font('Arial', 'B', 9)
        self.cell(w, 6, f"  {title}", 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        self.rect(x, y, w, h)

def generar_pdf_estilo_pro(cliente, ancho, alto, sistema, total):
    pdf = PDF_Pro()
    pdf.add_page()
    
    # --- AJUSTE CRÍTICO DE COORDENADAS ---
    # Bajamos el inicio de los datos a Y=55 para que NO toque el logo ni la línea
    y_inicio = 55
    
    # Bloque Datos Presupuesto
    pdf.draw_box(10, y_inicio, 90, 25, "DATOS DEL PRESUPUESTO")
    pdf.set_font('Arial', '', 9)
    pdf.set_xy(12, y_inicio + 8)
    pdf.cell(80, 5, f"FECHA: {datetime.date.today()}", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, f"VALIDEZ: 15 Días naturales", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "PAGO: 50% Anticipo / 50% Fin de obra", 0, 1)

    # Bloque Datos Cliente
    pdf.draw_box(105, y_inicio, 95, 25, "DATOS DEL CLIENTE")
    pdf.set_xy(107, y_inicio + 8)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 5, f"CLIENTE: {cliente.upper()}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(107)
    pdf.cell(90, 5, "Servicio: Fabricación e Instalación", 0, 1)

    # Sección Técnica - Bajamos a Y=90
    y_tecnica = 90
    pdf.set_fill_color(*AZUL_ZARAGOZA)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y_tecnica)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 7, "  DISEÑO ESTIMADO", 1, 0, 'L', fill=True)
    pdf.cell(95, 7, "  ESPECIFICACIONES", 1, 1, 'L', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.rect(10, y_tecnica + 7, 90, 55) 
    pdf.set_xy(15, y_tecnica + 25)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(80, 5, f"Modelo: {sistema}", 0, 1, 'C')
    pdf.set_x(15)
    pdf.cell(80, 5, f"{ancho} mm x {alto} mm", 0, 1, 'C')

    pdf.set_xy(105, y_tecnica + 10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 6, f"{sistema}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(105)
    pdf.multi_cell(90, 5, f"* Aluminio: Calidad Zaragoza Pro\n* Medida: {ancho} x {alto} mm\n* Vidrio: Claro 6mm (Templado opcional)\n* Sellado: Hermético antihongos\n* Herrajes: Alta resistencia.")

    # Tabla de Costos - Bajamos a Y=160
    y_tabla = 160
    pdf.set_xy(10, y_tabla)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 8, "CONCEPTO", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "CANTIDAD", 1, 0, 'C', fill=True)
    pdf.cell(60, 8, "TOTAL", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 12, f"Trabajo Integral de {sistema}", 1)
    pdf.cell(30, 12, "1", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 12, f"$ {total:,.2f} MXN", 1, 1, 'C')

    # Footer / Notas
    pdf.set_xy(10, 185)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(190, 4, "Nota: Los precios incluyen materiales y mano de obra. Las medidas finales serán rectificadas en sitio antes de iniciar la producción.")

    return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT APP ---
st.title("📂 Sistema de Control VA Zaragoza")

with st.sidebar:
    st.header("Configuración")
    cliente = st.text_input("Cliente", "Kelly Zaragoza")
    tipo = st.selectbox("Estructura", ["Ventana Corrediza", "Ventana Fija", "Puerta Batiente", "Cancel de Baño"])
    ancho_mm = st.number_input("Ancho (mm)", value=1200)
    alto_mm = st.number_input("Alto (mm)", value=1000)
    total_venta = st.number_input("Precio Total (MXN)", value=2220.0)

if st.button("🚀 Generar y Descargar Presupuesto"):
    pdf_res = generar_pdf_estilo_pro(cliente, ancho_mm, alto_mm, tipo, total_venta)
    st.download_button(
        label="⬇️ Descargar PDF Profesional",
        data=pdf_res,
        file_name=f"Presupuesto_VAZ_{cliente}.pdf",
        mime="application/pdf"
    )
