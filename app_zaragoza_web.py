import streamlit as st
import mysql.connector
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import base64

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="VAZ Zaragoza - Ingeniería v6.0", layout="wide", page_icon="🏢")

def aplicar_estilos_pro():
    st.markdown("""
        <style>
        .main { background-color: #f8fafc; }
        .vaz-card {
            background: white; padding: 25px; border-radius: 15px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }
        .price-banner {
            background: #0f172a; color: #38bdf8; padding: 20px;
            border-radius: 12px; text-align: center; border: 1px solid #1e293b;
        }
        .stButton>button {
            width: 100%; background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            color: white; border-radius: 8px; border: none; padding: 12px; font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# --- CLASE DE INGENIERÍA DE PRODUCTO ---
class VAZEngine:
    @staticmethod
    def calcular_logica_produccion(ancho, alto, modelo, serie):
        """Calcula despiece y materiales basados en reglas de taller"""
        # Descuentos técnicos (ajustables según necesidad real)
        cortes = [
            {"Pieza": "Cabezal Superior", "Cant": 1, "Corte": f"{ancho - 12} mm"},
            {"Pieza": "Riel Inferior", "Cant": 1, "Corte": f"{ancho - 12} mm"},
            {"Pieza": "Jambas Laterales", "Cant": 2, "Corte": f"{alto} mm"},
            {"Pieza": "Traslapes/Enganches", "Cant": 2, "Corte": f"{alto - 45} mm"}
        ]
        
        materiales = [
            f"Perfiles de Aluminio {serie}",
            "Kit de Carretillas de Nylon",
            "Empaque de Vinil (Cola de Pato)",
            "Felpa de sellado perimetral",
            "Pijas y fijadores de acero inoxidable"
        ]
        return cortes, materiales

# --- GENERADOR DE PDF (ESTILO OFICIAL ZARAGOZA) ---
class ZaragozaPDF(FPDF):
    def header(self):
        # Encabezado institucional (Sin IVA)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'Expertos en Cancelería, Cristal Templado y Fachadas', 0, 1, 'C')
        self.cell(0, 5, 'Tehuacán, Puebla | Orden de Producción y Cotización', 0, 1, 'C')
        self.ln(5)
        self.line(10, 35, 200, 35)

def generar_pdf_oficial(datos):
    pdf = ZaragozaPDF()
    pdf.add_page()
    
    # Bloque de Cliente y Folio
    pdf.set_fill_color(248, 250, 252)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(130, 8, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', 1)
    pdf.cell(60, 8, f" FOLIO: {datos['folio']}", 1, 1, 'C', 1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(130, 7, f" Direccion de Obra: {datos['dir']}", 1)
    pdf.cell(60, 7, f" Fecha: {datetime.now().strftime('%d/%m/%Y')}", 1, 1, 'C')

    # Especificaciones del Producto
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(0, 8, " ESPECIFICACIONES DEL PRODUCTO", 0, 1, 'L', 1)
    pdf.set_font('Arial', '', 10)
    especs = f"Sistema: {datos['serie']} | Modelo: {datos['modelo']} | Color: {datos['color']} | Vidrio: {datos['vidrio']}"
    pdf.multi_cell(0, 8, especs, 1)

    # Tabla de Cortes para Taller (Descuentos Aplicados)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, "HOJA DE CORTES (MEDIDAS REALES CON DESCUENTO)", 0, 1)
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255)
    pdf.cell(80, 8, "PIEZA", 1, 0, 'C', 1)
    pdf.cell(40, 8, "CANTIDAD", 1, 0, 'C', 1)
    pdf.cell(70, 8, "MEDIDA DE CORTE", 1, 1, 'C', 1)
    
    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 10)
    for c in datos['cortes']:
        pdf.cell(80, 8, c['Pieza'], 1)
        pdf.cell(40, 8, str(c['Cant']), 1, 0, 'C')
        pdf.cell(70, 8, c['Corte'], 1, 1, 'C')

    # Desglose Económico (Sin IVA)
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(130, 12, "INVERSIÓN TOTAL NETO (SIN IVA)", 1, 0, 'R', 0)
    pdf.cell(60, 12, f"$ {datos['total']:,.2f} MXN", 1, 1, 'R', 1)
    
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 5, "\n* Esta cotización no incluye IVA.\n* Incluye materiales, herrajes y mano de obra de instalación.\n* Vigencia de presupuesto: 15 días naturales.", 0, 'R')

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DINÁMICA ---
def render_dibujo_tecnico(ancho, alto, color, modelo):
    colores_hex = {"Blanco": "#FFFFFF", "Negro": "#000000", "Natural": "#94a3b8", "Madera": "#78350f"}
    hex_c = colores_hex.get(color, "#000000")
    max_d = max(ancho, alto)
    scale = 300 / max_d if max_d > 0 else 1
    w, h = ancho * scale, alto * scale

    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; background:#f1f5f9; padding:20px; border-radius:15px; border:1px solid #cbd5e1;">
            <div style="width:{w}px; text-align:center; border-bottom:2px solid {hex_c}; color:{hex_c}; font-weight:bold; margin-bottom:5px;">{ancho} mm</div>
            <div style="display:flex; align-items:center;">
                <div style="width:{w}px; height:{h}px; border:10px solid {hex_c}; background:rgba(186,230,253,0.3); display:flex; align-items:center; justify-content:center;">
                    <span style="font-size:10px; font-weight:bold; background:white; padding:2px 5px; border-radius:3px; border:1px solid {hex_c};">{modelo}</span>
                </div>
                <div style="height:{h}px; border-left:2px solid {hex_c}; margin-left:10px; display:flex; align-items:center; padding-left:5px; color:{hex_c}; font-weight:bold;">{alto} mm</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PRINCIPAL ---
def main():
    aplicar_estilos_pro()
    st.title("🏢 VAZ Zaragoza - Pro Engineering Suite")
    
    col_izq, col_der = st.columns([1, 1.2])

    with col_izq:
        with st.container():
            st.markdown('<div class="vaz-card">', unsafe_allow_html=True)
            st.subheader("📋 Datos del Proyecto")
            nombre = st.text_input("Nombre del Cliente")
            direccion = st.text_input("Dirección de Obra")
            
            st.divider()
            st.subheader("⚙️ Configuración Técnica")
            f1, f2 = st.columns(2)
            serie = f1.selectbox("Línea/Serie", ["Serie 20", "Serie 35", "Eurovent", "Templado"])
            modelo = f2.selectbox("Modelo", ["Ventana Corrediza", "Puerta Batiente", "Fijo", "Mosquitero"])
            
            color = st.selectbox("Acabado de Aluminio", ["Blanco", "Negro", "Natural", "Madera"])
            
            d1, d2, d3 = st.columns(3)
            ancho = d1.number_input("Ancho (mm)", min_value=100, value=1200)
            alto = d2.number_input("Alto (mm)", min_value=100, value=1200)
            vidrio = d3.selectbox("Vidrio", ["6mm Claro", "6mm Filtrasol", "10mm Templado"])
            st.markdown('</div>', unsafe_allow_html=True)

    with col_der:
        st.markdown('<div class="vaz-card">', unsafe_allow_html=True)
        st.subheader("📐 Validación y Gráficos")
        render_dibujo_tecnico(ancho, alto, color, modelo)
        
        # Cálculos de Negocio
        area_m2 = (ancho * alto) / 1000000
        precios_m2 = {"Serie 20": 1350, "Serie 35": 1750, "Eurovent": 2900, "Templado": 3600}
        total_neto = (area_m2 * precios_m2[serie] * 1.50) * (1.25 if color == "Madera" else 1.0)
        
        st.markdown(f"""
            <div class="price-banner">
                <small>INVERSIÓN TOTAL (SIN IVA)</small>
                <h2 style="margin:0;">${total_neto:,.2f} MXN</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Despiece en pantalla
        st.write("🔧 **Cortes de Taller:**")
        cortes, materiales = VAZEngine.calcular_logica_produccion(ancho, alto, modelo, serie)
        st.dataframe(pd.DataFrame(cortes), hide_index=True)

        if st.button("💾 GENERAR ORDEN Y PDF OFICIAL"):
            if nombre:
                folio = f"VAZ-{random.randint(1000, 9999)}"
                datos_finales = {
                    'nombre': nombre, 'dir': direccion, 'serie': serie, 
                    'modelo': modelo, 'color': color, 'vidrio': vidrio, 
                    'ancho': ancho, 'alto': alto, 'total': total_neto,
                    'folio': folio, 'cortes': cortes, 'materiales': materiales
                }
                
                pdf_bytes = generar_pdf_oficial(datos_finales)
                st.success(f"¡Cotización {folio} lista!")
                st.download_button(
                    label="📥 Descargar PDF (Formato Oficial)",
                    data=pdf_bytes,
                    file_name=f"VAZ_{folio}_{nombre.replace(' ','_')}.pdf",
                    mime="application/pdf"
                )
                
                # Vista previa del PDF
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.error("Por favor, ingresa el nombre del cliente.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
