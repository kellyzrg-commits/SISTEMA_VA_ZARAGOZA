import streamlit as st
import pandas as pd

# Configuración de la página para que se vea bien en celular
st.set_page_config(page_title="Zaragoza Gestión", page_icon="🪟")

st.title("🪟 Vidrios y Aluminios Zaragoza")
st.markdown("---")

# Menú lateral para configuración de precios
with st.sidebar:
    st.header("⚙️ Configuración")
    password = st.text_input("Contraseña", type="password")
    if password == "Ztomi19%":
        st.success("Acceso permitido")
        precio_m2_vidrio = st.number_input("Precio Vidrio m2", value=450.0)
    else:
        st.warning("Introduce la contraseña para editar precios")

# Cuerpo principal
col1, col2 = st.columns(2)

with col1:
    ancho = st.number_input("Ancho Total (metros)", min_value=0.1, step=0.01, format="%.2f")
with col2:
    alto = st.number_input("Alto Total (metros)", min_value=0.1, step=0.01, format="%.2f")

tipo = st.selectbox("Tipo de Ventana", ["Corrediza", "Fija"])

if st.button("Calcular Presupuesto y Cortes", use_container_width=True):
    # Convertir a cm
    L = ancho * 100
    H = alto * 100
    
    # --- FÓRMULAS FINALES ---
    # Marco
    m_sup_inf = L
    m_laterales = H - 2.8
    
    # Hojas
    if tipo == "Corrediza":
        h_ancho = (L - 18) / 2
        h_alto = H - 4.0
    else:
        h_ancho = (L - 18) / 2
        h_alto = H - 3.0

    # Mostrar Resultados de manera elegante
    st.subheader(f"📊 Reporte: Ventana {tipo}")
    
    st.info("🛠️ **Medidas de Corte (Aluminio)**")
    st.write(f"- **Chambrana Sup. y Riel Inf.:** 2 piezas de {m_sup_inf} cm")
    st.write(f"- **Chambranas Laterales:** 2 piezas de {m_laterales:.1f} cm")
    st.write(f"- **Cabezales y Zoclos:** 4 piezas de {h_ancho:.1f} cm")
    st.write(f"- **Cercos y Traslapes:** 4 piezas de {h_alto:.1f} cm")
    
    # Cotización rápida (ajusta la lógica de dinero según necesites)
    st.success(f"💰 **Presupuesto Estimado:** $ {(L+H)*3.5:.2f} MXN")