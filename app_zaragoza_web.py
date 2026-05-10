import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import base64

# --- SETTINGS & ADVANCED UI CONFIG ---
st.set_page_config(
    page_title="VAZ Zaragoza Engineering System",
    page_icon="🏢",
    layout="wide"
)

def apply_industrial_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;600;800&display=swap');
        
        :root {
            --vaz-bg: #0a0e14;
            --vaz-surface: #161b22;
            --vaz-accent: #00d2ff;
            --vaz-text: #e6edf3;
        }

        .stApp { background-color: var(--vaz-bg); color: var(--vaz-text); }
        
        .header-container {
            background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
            padding: 3rem; border-radius: 20px; border-bottom: 2px solid var(--vaz-accent);
            text-align: center; margin-bottom: 2rem; box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }

        .card-system {
            background: var(--vaz-surface); padding: 1.5rem; border-radius: 12px;
            border: 1px solid #30363d; margin-bottom: 1rem;
        }

        .hud-metric {
            background: #0d1117; padding: 1.2rem; border-radius: 10px;
            border: 1px solid var(--vaz-accent); text-align: center;
        }

        .price-label {
            color: var(--vaz-accent); font-size: 2.5rem; font-weight: 800;
            text-shadow: 0 0 15px rgba(0,210,255,0.3); font-family: 'JetBrains Mono';
        }

        /* Botones de Grado de Ingeniería */
        .stButton>button {
            width: 100%; background: transparent; color: var(--vaz-accent);
            border: 1px solid var(--vaz-accent); border-radius: 8px;
            padding: 1rem; font-weight: bold; text-transform: uppercase;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: var(--vaz-accent); color: #000; box-shadow: 0 0 20px var(--vaz-accent);
        }
        </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC CONTROLLER (OOP) ---
class ProductionEngine:
    """Motor de cálculo y despiece paramétrico."""
    MODELS = {
        "Serie 20": {"h": 12, "v": 45, "cost": 1680},
        "Serie 35": {"h": 15, "v": 48, "cost": 2100},
        "Eurovent": {"h": 10, "v": 40, "cost": 3450}
    }

    @staticmethod
    def generate_cut_list(w, h, model):
        p = ProductionEngine.MODELS.get(model)
        return [
            {"Componente": "Cabezal Superior", "Cant": 1, "Corte": f"{w - p['h']} mm"},
            {"Componente": "Riel Inferior", "Cant": 1, "Corte": f"{w - p['h']} mm"},
            {"Componente": "Jamba Lateral", "Cant": 2, "Corte": f"{h} mm"},
            {"Componente": "Traslape/Enganche", "Cant": 2, "Corte": f"{h - p['v']} mm"}
        ]

# --- DOCUMENT GENERATOR (PDF DOM) ---
class VAZReport(FPDF):
    def header(self):
        self.set_font('Courier', 'B', 18)
        self.set_text_color(20, 30, 50)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Courier', 'I', 10)
        self.cell(0, 5, 'Expertos en canceleria de aluminio, cristal templado, fachadas integrales y mucho mas...', 0, 1, 'C')
        self.ln(10)
        self.line(10, 35, 200, 35)

def build_pdf(data):
    pdf = VAZReport()
    pdf.add_page()
    pdf.set_font('Courier', 'B', 12)
    pdf.cell(130, 10, f"CLIENTE: {data['client'].upper()}", 1)
    pdf.cell(60, 10, f"FOLIO: {data['folio']}", 1, 1, 'C')
    
    pdf.ln(10)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255)
    pdf.cell(100, 10, " COMPONENTE", 1, 0, 'L', 1)
    pdf.cell(90, 10, " MEDIDA CORTE TALLER", 1, 1, 'C', 1)
    
    pdf.set_text_color(0)
    pdf.set_font('Courier', '', 10)
    for c in data['cuts']:
        pdf.cell(100, 9, f" {c['Componente']}", 1)
        pdf.cell(90, 9, c['Corte'], 1, 1, 'C')

    pdf.ln(15)
    pdf.set_font('Courier', 'B', 15)
    pdf.cell(120, 15, "COSTO TOTAL ", 1, 0, 'R')
    pdf.cell(70, 15, f"$ {data['total']:,.2f} MXN ", 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# --- DATA VISUALIZATION COMPONENT ---
def render_blueprint(w, h, color):
    colors = {"Blanco": "#ffffff", "Negro": "#000000", "Natural": "#848d95", "Madera": "#5d2f0e"}
    hex_c = colors.get(color, "#000")
    
    # Proporcionalidad Dinámica
    ratio = w / h if h != 0 else 1
    w_px = 350 if ratio >= 1 else 350 * ratio
    h_px = 350 / ratio if ratio >= 1 else 350

    st.markdown(f"""
        <div style="background:#0d1117; padding:40px; border-radius:20px; display:flex; flex-direction:column; align-items:center; border:1px solid #30363d;">
            <div style="width:{w_px}px; text-align:center; border-bottom:2px solid var(--vaz-accent); margin-bottom:10px; color:#fff; font-family:'JetBrains Mono';">{w} mm</div>
            <div style="display:flex; align-items:center;">
                <div style="width:{w_px}px; height:{h_px}px; border:14px solid {hex_c}; background:rgba(0,210,255,0.15); box-shadow:0 0 30px rgba(0,210,255,0.1); border-radius:4px;"></div>
                <div style="height:{h_px}px; border-left:2px solid var(--vaz-accent); margin-left:15px; padding-left:10px; color:#fff; display:flex; align-items:center; font-family:'JetBrains Mono';">{h} mm</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- ENTRY POINT ---
def main():
    apply_industrial_theme()
    
    st.markdown('<div class="header-container"><h1>VAZ ZARAGOZA ENTERPRISE</h1><p>v8.0 | Advanced Production & Costing Intelligence</p></div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.3], gap="large")

    with left:
        st.markdown('<div class="card-system">', unsafe_allow_html=True)
        st.subheader("⚙️ Configuración de Parámetros")
        client = st.text_input("Customer Identity")
        address = st.text_input("Project Location")
        
        col1, col2 = st.columns(2)
        model = col1.selectbox("Product Line", ["Serie 20", "Serie 35", "Eurovent"])
        color = col2.selectbox("Frame Finish", ["Blanco", "Negro", "Natural", "Madera"])
        
        w = st.number_input("Width (mm)", min_value=100, value=1200)
        h = st.number_input("Height (mm)", min_value=100, value=1500)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card-system">', unsafe_allow_html=True)
        render_blueprint(w, h, color)
        
        # Procesamiento de Data
        area = (w * h) / 1000000
        total = (area * ProductionEngine.MODELS[model]['cost']) * (1.3 if color == "Madera" else 1.0)
        cuts = ProductionEngine.generate_cut_list(w, h, model)

        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.markdown(f'<div class="hud-metric">Surface Area<br><b style="font-size:1.4rem;">{area:.3f} m²</b></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="hud-metric">Investment Total<br><span class="price-label">${total:,.2f}</span></div>', unsafe_allow_html=True)
        
        st.write("### 🛠️ Production Cutting Matrix")
        st.table(pd.DataFrame(cuts))

        if st.button("🚀 EXECUTE & GENERATE OFFICIAL PDF"):
            if client:
                folio = f"VAZ-{random.randint(10000, 99999)}"
                pdf_bytes = build_pdf({'client': client, 'folio': folio, 'total': total, 'cuts': cuts})
                
                st.download_button("📥 DOWNLOAD MASTER PDF", pdf_bytes, f"{folio}.pdf", "application/pdf")
                
                # Renderizado de PDF
                b64 = base64.b64encode(pdf_bytes).decode()
                st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="450"></iframe>', unsafe_allow_html=True)
            else:
                st.error("Authentication Error: Client identity is required.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
