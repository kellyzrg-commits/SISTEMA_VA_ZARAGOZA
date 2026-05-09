import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Generador de Presupuestos", layout="wide")

# Color Institucional (Azul Marino Zaragoza)
AZUL_ZARAGOZA = (24, 46, 82)

class PDF_Pro(FPDF):
    def header(self):
        # Intentar cargar el logo reemplazado
        logo_path = os.path.join("assets", "logo_zaragoza.png")
        
        if os.path.exists(logo_path):
            # Posicionamos el logo. 65mm de ancho para que se lea bien el texto interno.
            self.image(logo_path, 10, 8, 65) 
        
        # Información de contacto alineada a la derecha
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*AZUL_ZARAGOZA)
        self.set_xy(120, 10)
        self.cell(80, 5, "VIDRIOS Y ALUMINIOS ZARAGOZA", 0, 1, 'R')
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        self.set_x(120)
        self.cell(80, 4, "Cancelaría de Aluminio y Cristal", 0, 1, 'R')
        self.set_x(120)
        self.cell(80, 4, "Tehuacán, Puebla", 0, 1, 'R')
        
        # LÍNEA DIVISORIA: La bajamos a 48mm para que el logo nuevo no la toque
        self.set_draw_color(*AZUL_ZARAGOZA)
        self.set_line_width(0.6)
        self.line(10, 48, 200, 48)

    def draw_box(self, x, y, w, h, title):
        # Dibujar encabezado de sección azul
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
    
    # --- AJUSTE DE COORDENADAS PARA EVITAR ENCIMAMIENTO ---
    # Empezamos el contenido en Y=55 (7mm debajo de la línea divisoria)
    y_bloque1 = 55
    
    # Bloque 1: Datos del Presupuesto
    pdf.draw_box(10, y_bloque1, 90, 25, "DATOS DEL PRESUPUESTO")
    pdf.set_font('Arial', '', 9)
    pdf.set_xy(12, y_bloque1 + 8)
    pdf.cell(80, 5, f"FECHA: {datetime.date.today()}", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "VALIDEZ: 15 Días naturales", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "PAGO: 50% Anticipo / 50% Finalizar", 0, 1)

    # Bloque 2: Datos del Cliente
    pdf.draw_box(105, y_bloque1, 95, 25, "DATOS DEL CLIENTE")
    pdf.set_xy(107, y_bloque1 + 8)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 5, f"CLIENTE: {cliente.upper()}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(107)
    pdf.cell(90, 5, "Incluye: Entrega e Instalación", 0, 1)

    # Bloque 3: Especificaciones Técnicas (Bajamos a Y=90)
    y_tecnica = 90
    pdf.set_fill_color(*AZUL_ZARAGOZA)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y_tecnica)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 7, "  DISEÑO ESTIMADO", 1, 0, 'L', fill=True)
    pdf.cell(95, 7, "  DESCRIPCIÓN TÉCNICA", 1, 1, 'L', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.rect(10, y_tecnica + 7, 90, 55) # Cuadro para dibujo
    pdf.set_xy(15, y_tecnica + 25)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(80, 5, f"Modelo Sugerido: {sistema}", 0, 1, 'C')
    pdf.set_x(15)
    pdf.cell(80, 5, f"Dimensión: {ancho} x {alto} mm", 0, 1, 'C')

    # Detalles a la derecha
    pdf.set_xy(105, y_tecnica + 10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 6, f"{sistema}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(105)
    pdf.multi_cell(90, 5, f"* Aluminio de alta resistencia\n* Medida: {ancho} x {alto} mm\n* Vidrio: Claro 6mm\n* Sellado: Silicón de grado estructural\n* Herrajes: Línea premium.")

    # Bloque 4: Tabla de Costos (Y=160)
    y_tabla = 160
    pdf.set_xy(10, y_tabla)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 8, "CONCEPTO", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "CANT.", 1, 0, 'C', fill=True)
    pdf.cell(60, 8, "TOTAL NETO", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 12, f"Suministro e Instalación de {sistema}", 1)
    pdf.cell(30, 12, "1", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(60, 12, f"$ {total:,.2f} MXN", 1, 1, 'C')

    # Footer
    pdf.set_xy(10, 185)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(190, 4, "Nota: Este presupuesto no incluye IVA. Las medidas son rectificadas en obra por nuestro personal técnico antes de la fabricación.")

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🛡️ Panel de Ventas - Vidrios y Aluminios Zaragoza")

col1, col2 = st.columns(2)
with col1:
    cliente = st.text_input("Nombre del Cliente", "Kelly Zaragoza")
    sistema = st.selectbox("Producto", ["Ventana Corrediza", "Ventana Fija", "Puerta Batiente"])
with col2:
    ancho = st.number_input("Ancho (mm)", 1200)
    alto = st.number_input("Alto (mm)", 1000)
    total = st.number_input("Precio Final", 2220.0)

if st.button("✅ Crear Nota Profesional"):
    pdf_output = generar_pdf_vaz(cliente, ancho, alto, sistema, total)
    st.download_button(
        label="💾 Descargar PDF",
        data=pdf_output,
        file_name=f"Presupuesto_{cliente}.pdf",
        mime="application/pdf"
    )
