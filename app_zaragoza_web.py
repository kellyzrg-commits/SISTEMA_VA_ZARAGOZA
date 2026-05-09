import streamlit as st
import mysql.connector
import pandas as pd
from fpdf import FPDF
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema VA Zaragoza", layout="wide", page_icon="🪟")

# --- ESTILOS CSS PARA INTERFAZ PROFESIONAL ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    .catalogo-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        background-color: white;
        margin-bottom: 20px;
    }
    .diseno-box {
        border: 4px solid #333;
        background-color: #e3f2fd;
        margin: auto;
        display: flex;
        position: relative;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A NUBE (AIVEN) ---
def crear_conexion():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
    except:
        return None

# --- GENERACIÓN DE PDF ---
def generar_pdf(cliente, ancho, alto, sistema, df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Presupuesto: Vidrios y Aluminios Zaragoza", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Cliente: {cliente} | Sistema: {sistema}", ln=True, align='L')
    pdf.cell(200, 10, f"Medidas: {ancho}cm x {alto}cm", ln=True, align='L')
    
    # Tabla de despiece
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(60, 10, "Componente", 1)
    pdf.cell(40, 10, "Medida (cm)", 1)
    pdf.cell(30, 10, "Cantidad", 1)
    pdf.cell(60, 10, "Corte", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 10)
    for i, row in df.iterrows():
        pdf.cell(60, 10, str(row['Componente']), 1)
        pdf.cell(40, 10, str(row['Medida (cm)']), 1)
        pdf.cell(30, 10, str(row['Cantidad']), 1)
        pdf.cell(60, 10, str(row['Observaciones']), 1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

# --- LÓGICA DE NAVEGACIÓN ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'Catálogo'

# --- VISTA: CATÁLOGO ---
if st.session_state.pagina == 'Catálogo':
    st.title("📂 Catálogo de Diseños")
    st.write("Selecciona un modelo para comenzar la cotización o mostrar al cliente.")
    
    col1, col2, col3 = st.columns(3)
    
    sistemas = [
        {"nombre": "Ventana Corrediza", "img": "https://via.placeholder.com/150?text=Corrediza", "id": "corrediza"},
        {"nombre": "Ventana Fija", "img": "https://via.placeholder.com/150?text=Fija", "id": "fija"},
        {"nombre": "Puerta Batiente", "img": "https://via.placeholder.com/150?text=Puerta", "id": "puerta"}
    ]
    
    cols = [col1, col2, col3]
    for i, sys in enumerate(sistemas):
        with cols[i]:
            st.markdown(f'<div class="catalogo-card"><img src="{sys["img"]}" width="100%"><h3>{sys["nombre"]}</h3></div>', unsafe_allow_html=True)
            if st.button(f"Cotizar {sys['nombre']}", key=sys['id']):
                st.session_state.sistema_sel = sys['nombre']
                st.session_state.pagina = 'Cotizador'
                st.rerun()

# --- VISTA: COTIZADOR ---
elif st.session_state.pagina == 'Cotizador':
    st.sidebar.button("⬅️ Volver al Catálogo", on_click=lambda: st.session_state.update({"pagina": "Catálogo"}))
    st.title(f"🧮 Cotizador: {st.session_state.sistema_sel}")

    with st.container():
        col_f, col_m = st.columns([1, 1])
        with col_f:
            cliente = st.text_input("Nombre del Cliente", "Venta Mostrador")
            ancho = st.number_input("Ancho Total (cm)", min_value=10.0, value=100.0, step=0.1)
            alto = st.number_input("Alto Total (cm)", min_value=10.0, value=100.0, step=0.1)
        
        with col_m:
            # REPRESENTACIÓN GRÁFICA DINÁMICA
            st.write("### Vista Previa")
            ancho_px = min(ancho * 2, 300)
            alto_px = min(alto * 2, 300)
            st.markdown(f"""
                <div class="diseno-box" style="width: {ancho_px}px; height: {alto_px}px;">
                    <div style="border-right: 2px solid #333; width: 50%; height: 100%; display: flex; align-items: center; justify-content: center;">O</div>
                    <div style="width: 50%; height: 100%; display: flex; align-items: center; justify-content: center;">X</div>
                    <div style="position: absolute; bottom: -25px; width: 100%; text-align: center; font-weight: bold;">{ancho} cm</div>
                    <div style="position: absolute; left: -70px; top: 45%; font-weight: bold; transform: rotate(-90deg);">{alto} cm</div>
                </div>
            """, unsafe_allow_html=True)

    # CÁLCULOS CON FÓRMULAS CORREGIDAS
    zoclo_medida = (ancho - 18) / 2 #
    
    despiece_data = {
        "Componente": ["Cabezal", "Sillar", "Jambas", "Zoclos", "Traslapes"],
        "Medida (cm)": [ancho, ancho, alto, zoclo_medida, alto - 5],
        "Cantidad": [1, 1, 2, 2, 2],
        "Observaciones": ["Corte Recto", "Corte Recto", "Corte Recto", "Descuento Aplicado", "Corte Recto"]
    }
    df = pd.DataFrame(despiece_data)
    
    st.write("### 📝 Despiece Automático")
    st.table(df)

    if st.button("💾 Guardar y Generar PDF"):
        pdf_bytes = generar_pdf(cliente, ancho, alto, st.session_state.sistema_sel, df)
        st.download_button(label="📥 Descargar Reporte PDF", data=pdf_bytes, file_name=f"Presupuesto_{cliente}.pdf", mime="application/pdf")
        # Aquí puedes llamar a crear_conexion() para guardar en Aiven
