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
            # 50 de ancho es el tamaño perfecto para que sea legible y proporcional
            self.image(logo_path, 10, 10, 50) 
        else:
            self.set_font('Arial', 'B', 15)
            self.set_text_color(*AZUL_ZARAGOZA)
            self.cell(60, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA')
        
        # Información de la Empresa (Alineada a la derecha)
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
        
        # Línea divisoria elegante (un poco más abajo para dar espacio al logo)
        self.set_draw_color(*AZUL_ZARAGOZA)
        self.set_line_width(0.5)
        self.line(10, 42, 200, 42)

    def draw_box(self, x, y, w, h, title):
        # Fondo de las barras de título
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
    
    # --- COORDENADAS REVISADAS PARA EVITAR ENCIMAMIENTO ---
    # Bajamos los cuadros de datos a la posición Y=52 (10mm debajo de la línea)
    y_bloque_superior = 52
    
    # Bloque Datos Presupuesto
    pdf.draw_box(10, y_bloque_superior, 90, 25, "DATOS DEL PRESUPUESTO")
    pdf.set_font('Arial', '', 9)
    pdf.set_xy(12, y_bloque_superior + 8)
    pdf.cell(80, 5, f"FECHA: {datetime.date.today()}", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, f"VALIDEZ: 15 Días", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "FORMA DE PAGO: 50% Anticipo / 50% Final", 0, 1)

    # Bloque Datos Cliente
    pdf.draw_box(105, y_bloque_superior, 95, 25, "DATOS DEL CLIENTE")
    pdf.set_xy(107, y_bloque_superior + 8)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 5, f"CLIENTE: {cliente.upper()}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(107)
    pdf.cell(90, 5, "Entrega e Instalación Incluida", 0, 1)

    # --- SECCIÓN TÉCNICA (Bajamos a Y=87) ---
    y_tecnica = 87
    pdf.set_fill_color(*AZUL_ZARAGOZA)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y_tecnica)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 7, "  DISEÑO ESTIMADO", 1, 0, 'L', fill=True)
    pdf.cell(95, 7, "  DESCRIPCIÓN", 1, 1, 'L', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.rect(10, y_tecnica + 7, 90, 55) # Espacio para el gráfico
    pdf.set_xy(15, y_tecnica + 25)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(80, 5, f"Representación: {sistema}", 0, 1, 'C')
    pdf.set_x(15)
    pdf.cell(80, 5, f"{ancho} mm x {alto} mm", 0, 1, 'C')

    # Descripción detallada
    pdf.set_xy(105, y_tecnica + 10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 6, f"{sistema}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(105)
    pdf.multi_cell(90, 5, f"* Serie: Línea comercial de aluminio\n* Color: Natural / Negro / Blanco\n* Medida: {ancho} x {alto} mm\n* Vidrio: Claro 6mm\n* Incluye: Herrajes y sellado.")

    # --- TABLA DE COSTOS (Bajamos a Y=152) ---
    y_tabla = 152
    pdf.set_xy(10, y_tabla)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 8, "CONCEPTO", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "CANTIDAD", 1, 0, 'C', fill=True)
    pdf.cell(60, 8, "TOTAL NETO", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 12, f"Suministro e Instalación de {sistema}", 1)
    pdf.cell(30, 12, "1", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 12, f"$ {total:,.2f} MXN", 1, 1, 'C')

    # Nota final
    pdf.set_xy(10, 180)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(190, 4, "Este presupuesto es una estimación técnica basada en las medidas proporcionadas por el cliente. Precios sujetos a cambios sin previo aviso. No incluye IVA.")

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ STREAMLIT ---
st.title("🛡️ Sistema de Presupuestos VA Zaragoza")

cliente = st.text_input("Nombre del Cliente", "Kelly Zaragoza")
sistema = st.selectbox("Tipo de Trabajo", ["Ventana Corrediza", "Ventana Fija", "Puerta de Baño"])
ancho = st.number_input("Ancho (mm)", value=1200)
alto = st.number_input("Alto (mm)", value=1000)
precio_total = st.number_input("Costo Total (MXN)", value=2220)

if st.button("📄 Generar Nota de Venta"):
    pdf_bytes = generar_pdf_estilo_pro(cliente, ancho, alto, sistema, precio_total)
    st.download_button(
        label="⬇️ Descargar PDF",
        data=pdf_bytes,
        file_name=f"Presupuesto_{cliente}.pdf",
        mime="application/pdf"
    )
