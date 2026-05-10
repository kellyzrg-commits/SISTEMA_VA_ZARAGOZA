import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import base64

# --- SETTINGS & ASSETS ---
st.set_page_config(
    page_title="VAZ Zaragoza Enterprise | v7.2",
    page_icon="🏢",
    layout="wide"
)

# --- ARCHITECTURAL STYLING (CSS INJECTION) ---
def inject_enterprise_ui():
    st.markdown("""
        <style>
        :root {
            --primary-dark: #0f172a;
            --accent-cyan: #22d3ee;
            --surface-white: #ffffff;
        }
        
        .stApp { background-color: #f8fafc; }
        
        /* Dashboard Container */
        .enterprise-container {
            background: var(--primary-dark);
            padding: 2.5rem;
            border-radius: 24px;
            color: white;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            margin-bottom: 2rem;
            border-bottom: 4px solid var(--accent-cyan);
        }

        /* Logic Cards */
        .logic-card {
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s;
        }
        
        /* Metric HUD */
        .metric-hud {
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border-top: 3px solid var(--primary-dark);
        }

        .price-highlight {
            color: #0891b2;
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -1px;
        }

        /* Specialized Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
            color: #22d3ee;
            border: 1px solid #22d3ee;
            border-radius: 10px;
            font-weight: 700;
            height: 3.5rem;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

# --- BUSINESS LOGIC CONTROLLER ---
class VAZController:
    """Clase controladora encargada de la persistencia lógica y despiece."""
    
    ENGINEERING_DEFAULTS = {
        "Serie 20": {"h_offset": 12, "v_offset": 45, "base_cost": 1550},
        "Serie 35": {"h_offset": 15, "v_offset": 48, "base_cost": 1980},
        "Eurovent": {"h_offset": 10, "v_offset": 40, "base_cost": 3250}
    }

    @classmethod
    def process_work_order(cls, width, height, series, finish):
        params = cls.ENGINEERING_DEFAULTS.get(series)
        
        # Despiece algorítmico
        cutting_list = [
            {"Elemento": "Cerco Superior/Riel", "Cant": 2, "Corte": width - params['h_offset']},
            {"Elemento": "Jambas Perimetrales", "Cant": 2, "Corte": height},
            {"Elemento": "Traslapes Centrales", "Cant": 2, "Corte": height - params['v_offset']},
            {"Elemento": "Zoclo de Refuerzo", "Cant": 2, "Corte": width - params['h_offset']}
        ]
        
        # Cálculo volumétrico y financiero
        area = (width * height) / 1000000
        multiplier = 1.35 if finish == "Madera" else 1.0
        final_cost = (area * params['base_cost']) * multiplier
        
        return cutting_list, area, final_cost

# --- PDF GENERATION DOM ---
class ZaragozaReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 11)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, 'Expertos en canceleria de aluminio, cristal templado, fachadas integrales y mucho mas...', 0, 1, 'C')
        self.set_font('Helvetica', '', 9)
        self.cell(0, 5, 'Tehuacán, Puebla | Centro de Ingeniería', 0, 1, 'C')
        self.ln(10)
        self.line(10, 42, 200, 42)

def generate_secure_pdf(payload):
    pdf = ZaragozaReport()
    pdf.add_page()
    
    # Metadata Block
    pdf.set_fill_color(248, 250, 252)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(130, 10, f" CLIENTE: {payload['client'].upper()}", 1, 0, 'L', 1)
    pdf.cell(60, 10, f" FOLIO: {payload['id']}", 1, 1, 'C', 1)
    
    # Specs Table
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, "ESPECIFICACIONES TÉCNICAS", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    content = f"Línea: {payload['series']} | Acabado: {payload['finish']} | Cristal: {payload['glass']} | Dimensión: {payload['w']}x{payload['h']} mm"
    pdf.multi_cell(0, 10, content, 1)

    # Cutting Matrix
    pdf.ln(5)
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255)
    pdf.cell(100, 10, " COMPONENTE DE TALLER", 1, 0, 'L', 1)
    pdf.cell(90, 10, " CORTE NOMINAL", 1, 1, 'C', 1)
    
    pdf.set_text_color(0)
    for item in payload['cuts']:
        pdf.cell(100, 9, f" {item['Elemento']}", 1)
        pdf.cell(90, 9, f"{item['Corte']} mm", 1, 1, 'C')

    # Financial Total
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_fill_color(230, 245, 255)
    pdf.cell(130, 14, "COSTO TOTAL ", 1, 0, 'R', 1)
    pdf.cell(60, 14, f"$ {payload['total']:,.2f} MXN ", 1, 1, 'R', 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- DATA VISUALIZATION COMPONENT ---
def render_tech_blueprint(w, h, color_name):
    hex_map = {"Blanco": "#ffffff", "Negro": "#020617", "Natural": "#64748b", "Madera": "#78350f"}
    c = hex_map.get(color_name, "#0f172a")
    
    aspect_ratio = w / h if h != 0 else 1
    w_px = 350 if aspect_ratio >= 1 else 350 * aspect_ratio
    h_px = 350 / aspect_ratio if aspect_ratio >= 1 else 350

    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; background: #e2e8f0; padding: 40px; border-radius: 20px; border: 2px solid #cbd5e1;">
            <div style="width: {w_px}px; text-align: center; border-bottom: 2px solid #1e293b; margin-bottom: 15px; font-family: 'Courier New'; font-weight: bold; color: #1e293b;">{w} mm</div>
            <div style="display: flex; align-items: center;">
                <div style="width: {w_px}px; height: {h_px}px; border: 15px solid {c}; background: radial-gradient(circle, #bae6fd 0%, #7dd3fc 100%); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2);"></div>
                <div style="height: {h_px}px; border-left: 2px solid #1e293b; margin-left: 15px; display: flex; align-items: center; padding-left: 15px; font-family: 'Courier New'; font-weight: bold; color: #1e293b;">{h} mm</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN EXECUTION LAYER ---
def application_entrypoint():
    inject_enterprise_ui()
    
    st.markdown("""
        <div class="enterprise-container">
            <h1 style="margin:0; letter-spacing: -2px;">VAZ ZARAGOZA ENTERPRISE</h1>
            <p style="opacity: 0.8; font-weight: 400;">v7.2 Build 2026 | Sistema de Control de Producción y Presupuesto</p>
        </div>
    """, unsafe_allow_html=True)

    form_col, view_col = st.columns([1, 1.3], gap="large")

    with form_col:
        st.markdown('<div class="logic-card">', unsafe_allow_html=True)
        st.subheader("🖋️ Parámetros del Proyecto")
        client = st.text_input("Identificador del Cliente", placeholder="Nombre o Empresa")
        address = st.text_input("Ubicación Geográfica", placeholder="Ciudad, Obra")
        
        st.divider()
        st.subheader("⚙️ Atributos de Ingeniería")
        s_col, f_col = st.columns(2)
        serie = s_col.selectbox("Línea de Producción", ["Serie 20", "Serie 35", "Eurovent"])
        color = f_col.selectbox("Finish/Acabado", ["Blanco", "Negro", "Natural", "Madera"])
        
        w_col, h_col = st.columns(2)
        ancho = w_col.number_input("Ancho Nominal (mm)", min_value=100, value=1200)
        alto = h_col.number_input("Alto Nominal (mm)", min_value=100, value=1500)
        
        vidrio = st.selectbox("Especificación de Cristal", ["6mm Claro", "6mm Filtrasol", "10mm Templado", "Duovent"])
        st.markdown('</div>', unsafe_allow_html=True)

    with view_col:
        st.markdown('<div class="logic-card">', unsafe_allow_html=True)
        render_tech_blueprint(ancho, alto, color)
        
        # Data Processing via Controller
        cuts, area, total = VAZController.process_work_order(ancho, alto, serie, color)
        
        st.markdown("<br>", unsafe_allow_html=True)
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f'<div class="metric-hud">Superficie<br><b style="font-size:1.5rem;">{area:.3f} m²</b></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="metric-hud">Importe de Inversión<br><span class="price-highlight">${total:,.2f}</span></div>', unsafe_allow_html=True)
        
        st.write("### 🛠️ Work Order Matrix (Taller)")
        st.dataframe(pd.DataFrame(cuts), hide_index=True, use_container_width=True)

        if st.button("Generate & Sync Deployment"):
            if client:
                folio = f"VAZ-PRO-{random.randint(10000, 99999)}"
                payload = {
                    'client': client, 'id': folio, 'series': serie, 
                    'finish': color, 'glass': vidrio, 'w': ancho, 
                    'h': alto, 'total': total, 'cuts': cuts
                }
                binary_pdf = generate_secure_pdf(payload)
                
                st.download_button(
                    label="📥 Exportar Master PDF",
                    data=binary_pdf,
                    file_name=f"ORDEN_{folio}.pdf",
                    mime="application/pdf"
                )
                
                # PDF Rendering
                pdf_base64 = base64.b64encode(binary_pdf).decode()
                st.markdown(f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="500" type="application/pdf"></iframe>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Error de Validación: El campo 'Cliente' es mandatorio.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    application_entrypoint()
