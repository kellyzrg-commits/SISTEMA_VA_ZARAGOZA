import streamlit as st
import pandas as pd
from fpdf2 import FPDF# fpdf2 utiliza el mismo espacio de nombres, pero asegurémonos de que cargue bien
from datetime import datetime
import random
import base64
import matplotlib.pyplot as plt
import io

# ==========================================
# CONFIGURACIÓN DE LA APLICACIÓN (UI/UX)
# ==========================================
st.set_page_config(
    page_title="SISTEMA VA ZARAGOZA",
    page_icon="🏢",
    layout="wide"
)

# Estilos CSS - Minimalista Industrial Moderno (Azul Aluminio, Blanco y Negro)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #0f172a; font-weight: 700; }
    
    .card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .total-box {
        background-color: #0f172a;
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-top: 20px;
    }
    .total-box h2 { color: #00d2ff; margin: 0; font-size: 2.5rem; }
    
    .stButton>button {
        width: 100%;
        background-color: #0f172a;
        color: white;
        border: none;
        padding: 15px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1e293b; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.4); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# MOTOR DE INGENIERÍA Y COSTOS REALES
# ==========================================
class VAZ_Motor:
    # Costos aproximados de material por m2 en el mercado regional
    PRECIOS_BASE_M2 = {
        "Ventana Fijo-Corrediza 3\"": 1200.0,
        "Puerta de Aluminio 3\"": 1650.0
    }

    @staticmethod
    def calcular_precio_venta(ancho, alto, producto):
        # 1. Calcular el área en metros cuadrados
        area_m2 = (ancho * alto) / 1000000.0
        
        # 2. Obtener costo base del material
        costo_base = area_m2 * VAZ_Motor.PRECIOS_BASE_M2.get(producto, 1200.0)
        
        # 3. APLICAR EL 50% DE GANANCIA SOLICITADO
        # Multiplicar por 1.50 añade exactamente el 50% de margen de utilidad sobre el costo
        precio_final = costo_base * 1.50
        return area_m2, precio_final

    @staticmethod
    def generar_hoja_taller(ancho, alto, producto):
        """Implementación estricta de las fórmulas indicadas en milímetros (mm)"""
        cortes = []
        
        if producto == "Puerta de Aluminio 3\"":
            cortes = [
                {"Elemento": "Batiente Horizontal Superior (Contra Marco)", "Cant": 1, "Corte": f"{ancho - 13:.1f} mm", "Fórmula": "Ancho - 1.3 cm"},
                {"Elemento": "Batiente Vertical Lateral (Contra Marco)", "Cant": 2, "Corte": f"{alto - 13:.1f} mm", "Fórmula": "Alto - 1.3 cm"},
                {"Elemento": "Zoclo Inferior (Hoja)", "Cant": 1, "Corte": f"{ancho - 140:.1f} mm", "Fórmula": "Ancho - 14 cm"},
                {"Elemento": "Cabezal Superior (Hoja)", "Cant": 1, "Corte": f"{ancho - 140:.1f} mm", "Fórmula": "Ancho - 14 cm"},
                {"Elemento": "Cercos Laterales (Hoja)", "Cant": 2, "Corte": f"{alto - 26:.1f} mm", "Fórmula": "Alto - 2.6 cm"}
            ]
        elif producto == "Ventana Fijo-Corrediza 3\"":
            ancho_hoja_fija = (ancho - 18) / 2
            ancho_hoja_corrediza = (ancho - 18) / 2
            
            cortes = [
                {"Elemento": "Chambrana Superior (Marco)", "Cant": 1, "Corte": f"{ancho:.1f} mm", "Fórmula": "Medida Real"},
                {"Elemento": "Riel Inferior (Marco)", "Cant": 1, "Corte": f"{ancho:.1f} mm", "Fórmula": "Medida Real"},
                {"Elemento": "Chambranas Laterales (Marco)", "Cant": 2, "Corte": f"{alto - 28:.1f} mm", "Fórmula": "Alto - 2.8 cm"},
                {"Elemento": "Zoclo y Cabezal (Hoja Fija)", "Cant": 2, "Corte": f"{ancho_hoja_fija:.1f} mm", "Fórmula": "(Ancho - 18) / 2"},
                {"Elemento": "Cerco y Traslape (Hoja Fija)", "Cant": 2, "Corte": f"{alto - 30:.1f} mm", "Fórmula": "Alto - 3 cm"},
                {"Elemento": "Zoclo y Cabezal (Hoja Corrediza)", "Cant": 2, "Corte": f"{ancho_hoja_corrediza:.1f} mm", "Fórmula": "(Ancho - 18) / 2"},
                {"Elemento": "Cerco y Traslape (Hoja Corrediza)", "Cant": 2, "Corte": f"{alto - 40:.1f} mm", "Fórmula": "Alto - 4 cm"}
            ]
        return cortes

# ==========================================
# MOTOR GRÁFICO DE APERTURAS Y MEDIDAS
# ==========================================
def generar_dibujo_tecnico(ancho, alto, producto):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Dibujar marco perimetral externo
    marco = plt.Rectangle((0, 0), ancho, alto, fill=False, edgecolor='#0f172a', linewidth=3)
    ax.add_patch(marco)
    
    if "Ventana" in producto:
        mitad = ancho / 2
        # Separador de hojas (Fijo / Corredizo)
        ax.plot([mitad, mitad], [0, alto], color='#0f172a', linewidth=2)
        # Indicador de paño fijo (X) y deslizamiento (Flecha técnica)
        ax.text(mitad/2, alto/2, "FIJO", ha='center', va='center', color='gray', fontsize=10, weight='bold')
        ax.annotate('◄═══════', xy=(mitad + mitad/2, alto/2), ha='center', va='center', fontsize=12, color='#0f172a')
    elif "Puerta" in producto:
        # Dibujar sentido de apertura abatible con líneas punteadas industriales
        ax.plot([0, ancho, ancho], [0, alto/2, alto], color='gray', linestyle='--')
        ax.text(ancho/2, alto/2, "↻", ha='center', va='center', fontsize=24, color='#0f172a')

    # Acotaciones Dinámicas Automatizadas en Milímetros (mm)
    ax.annotate(f'{ancho} mm', xy=(ancho/2, alto + (alto*0.04)), ha='center', fontsize=11, color='#0f172a', weight='bold')
    ax.annotate(f'{alto} mm', xy=(-(ancho*0.05), alto/2), va='center', rotation=90, fontsize=11, color='#0f172a', weight='bold')

    ax.set_xlim(-ancho*0.1, ancho*1.1)
    ax.set_ylim(-alto*0.1, alto*1.15)
    ax.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close()
    return buf

# ==========================================
# MOTOR EXPORTADOR: PDF DOCUMENTAL
# ==========================================
class CotizacionPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, 'Presupuestos de Cancelería Residencial e Industrial', 0, 1, 'C')
        self.ln(6)
        self.line(10, 28, 200, 28)

def exportar_pdf_oficial(datos, img_buf):
    pdf = CotizacionPDF()
    pdf.add_page()
    
    # Bloque de cabecera comercial
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 244, 248)
    pdf.cell(130, 8, f" CLIENTE: {datos['cliente'].upper()}", 1, 0, 'L', 1)
    pdf.cell(60, 8, f" FOLIO: {datos['folio']}", 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 9)
    pdf.cell(130, 8, f" Dirección: {datos['direccion'] if datos['direccion'] else 'Tehuacán, Puebla'}", 1, 0, 'L')
    pdf.cell(60, 8, f" Emisión: {datetime.now().strftime('%d/%m/%Y')}", 1, 1, 'C')
    pdf.ln(6)
    
    # Contenedor de Especificaciones
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, "DETALLE DE LOS PRODUCTOS COTIZADOS:", 0, 1)
    pdf.set_font('Arial', '', 10)
    info_estructura = f"Estructura: {datos['producto']}\nMedidas de Fabricación: {datos['ancho']} mm de Ancho x {datos['alto']} mm de Alto\nAcabado / Color: {datos['color']} | Cristal Configurado: {datos['cristal']}"
    pdf.multi_cell(0, 6, info_estructura, border=1)
    
    # Incrustar renderizado gráfico de la pieza
    pdf.ln(4)
    with open("temp_pdf_render.png", "wb") as f:
        f.write(img_buf.getbuffer())
    pdf.image("temp_pdf_render.png", x=55, w=100)
    
    # Bloque Financiero Neto (Cumple regla: NO IVA, NO COSTOS INTERNOS)
    pdf.ln(6)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(120, 12, " TOTAL NETO A PAGAR ", 1, 0, 'R', 1)
    pdf.cell(70, 12, f"$ {datos['total']:,.2f} MXN ", 1, 1, 'R', 1)
    
    # Términos legales de aceptación comercial
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 4, "Esta cotización tiene una vigencia de 15 días naturales a partir de su fecha de emisión.", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# INTERFAZ DE USUARIO (STREAMLIT APP)
# ==========================================
def main():
    st.title("🏢 Vidrios y Aluminios Zaragoza")
    st.subheader("Motor de Ingeniería y Presupuestos")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.subheader("📝 Datos de Captura")
        cliente = st.text_input("Nombre del Cliente", placeholder="Ej. Juan Pérez")
        direccion = st.text_input("Ubicación de la Obra", placeholder="Tehuacán, Pue.")
        
        st.markdown("---")
        producto = st.selectbox("Seleccione el Producto", ["Ventana Fijo-Corrediza 3\"", "Puerta de Aluminio 3\""])
        color = st.selectbox("Color del Aluminio", ["Blanco", "Negro", "Natural", "Madera"])
        cristal = st.selectbox("Tipo de Cristal", ["Claro", "Filtrasol", "Esmerilado", "Templado"])
        
        st.markdown("**Dimensiones de Fabricación (Estricto en mm):**")
        col_w, col_h = st.columns(2)
        ancho = col_w.number_input("Ancho Total (mm)", min_value=100, max_value=6000, value=1200, step=1)
        alto = col_h.number_input("Alto Total (mm)", min_value=100, max_value=6000, value=1500, step=1)
    
    with c2:
        st.subheader("📊 Gráfico Técnico y Presupuesto")
        
        # Renderizado en tiempo real del dibujo
        img_buf = generar_dibujo_tecnico(ancho, alto, producto)
        st.image(img_buf, use_container_width=True)
        
        # Procesamiento financiero con el 50% de ganancia ya sumado
        area, total_venta = VAZ_Motor.calcular_precio_venta(ancho, alto, producto)
        
        st.markdown(f"""
            <div class="total-box">
                <p style="margin:0; font-size:13px; opacity:0.85;">Área Calculada: {area:.3f} m² | Margen: +50% Utilidad</p>
                <h2>$ {total_venta:,.2f} MXN</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Despliegue exclusivo de Taller (Protegido, no sale en el PDF del cliente)
        with st.expander("🛠️ Ver Lista de Cortes para Taller (Uso Interno)"):
            cortes_data = VAZ_Motor.generar_hoja_taller(ancho, alto, producto)
            st.table(pd.DataFrame(cortes_data))
            
   st.write("")
        if st.button("📄 GENERAR DOCUMENTO DE COTIZACIÓN"):
            if cliente:
                folio_vaz = f"VAZ-{random.randint(1000, 9999)}"
                datos_operacion = {
                    "cliente": cliente, "direccion": direccion, "folio": folio_vaz,
                    "producto": producto, "color": color, "cristal": cristal,
                    "ancho": ancho, "alto": alto, "total": total_venta
                }
                pdf_binario = exportar_pdf_oficial(datos_operacion, img_buf)
                st.success(f"¡Documento {folio_vaz} procesado con éxito!")
                st.download_button(
                    label="📥 Guardar PDF Oficial",
                    data=pdf_binario,
                    file_name=f"Cotizacion_{folio_vaz}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("⚠️ El campo 'Nombre del Cliente' es obligatorio para poder emitir el documento.")
                
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
