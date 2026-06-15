import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Spray Roaster Optimizer", layout="wide")
st.title("🔥 Spray Roaster Optimizer - HCl Regeneration")
st.markdown("**Herramienta profesional de diagnóstico y optimización** para plantas de regeneración de ácido clorhídrico")

# --- Sidebar - Entradas ---
with st.sidebar:
    st.header("Parámetros de Operación")
    
    caudal_total = st.slider("Caudal total CPL (l/min)", 35, 55, 45)
    picos_totales = st.slider("Picos totales", 8, 12, 10)
    diametro_pico = st.slider("Diámetro promedio de picos (mm)", 0.7, 2.4, 1.2, step=0.05)
    presion = st.slider("Presión de inyección (bar)", 6.5, 9.5, 8.0, step=0.1)
    temp_cpl = st.slider("Temperatura CPL (°C)", 80, 100, 93)
    temp_quemadores = st.number_input("Temperatura promedio quemadores (°C)", value=760)
    temp_cono = st.number_input("Temperatura cono inferior (°C)", value=580)
    o2_chimenea = st.number_input("% O₂ en chimenea", value=12.0)
    
    st.markdown("---")
    st.caption("Datos de operación actual - Ternium")

# --- Cálculos ---
caudal_por_pico = caudal_total / picos_totales

# Factor temperatura
factor_temp = max(0.83, min(0.92, 0.83 + (temp_cpl - 80) * 0.009))

# SMD (Sauter Mean Diameter) aproximado
smd = 1750 * (diametro_pico ** 0.5) / (presion ** 0.5) * factor_temp

# Exceso de aire aproximado
exceso_aire = max(3, min(25, (o2_chimenea - 3) * 4.5))

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🧮 Calculadora", "⚠️ Recomendaciones", "📖 Notas Técnicas"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Caudal por pico", f"{caudal_por_pico:.1f} l/min")
    with col2:
        st.metric("SMD", f"{smd:.0f} µm")
    with col3:
        st.metric("Exceso de aire", f"{exceso_aire:.1f} %")
    with col4:
        st.metric("Temp. Quemadores", f"{temp_quemadores} °C")
    
    # Gráfico SMD
    st.subheader("Efecto del diámetro y presión en SMD")
    df_graf = pd.DataFrame({
        "Diámetro (mm)": [0.7, 1.0, 1.2, 1.5, 2.0, 2.4],
        "SMD a 8 bar": [1750*(d**0.5)/(8**0.5)*factor_temp for d in [0.7,1.0,1.2,1.5,2.0,2.4]]
    })
    fig = px.line(df_graf, x="Diámetro (mm)", y="SMD a 8 bar", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Resultados de Cálculo")
    st.write(f"**Caudal por pico:** {caudal_por_pico:.2f} l/min")
    st.write(f"**SMD estimado:** {smd:.0f} µm")
    st.write(f"**Exceso de aire estimado:** {exceso_aire:.1f} %")
    
    # Evaluación de riesgos
    st.subheader("Evaluación de Riesgos")
    riesgos = []
    
    if smd > 170:
        riesgos.append(("🔴", "Tamaño de gota excesivo", "Riesgo alto de óxido húmedo y barro en cono", "Reducir diámetro de pico o aumentar presión"))
    if smd < 65:
        riesgos.append(("🔴", "Gota demasiado fina", "Riesgo de sobrecalentamiento y magnetita", "Aumentar diámetro de pico"))
    if temp_quemadores < 740:
        riesgos.append(("🔴", "Temperatura baja en quemadores", "Mala combustión y oxidación incompleta", "Aumentar combustible / revisar quemadores"))
    if temp_quemadores > 860:
        riesgos.append(("🟠", "Sobrecalentamiento", "Riesgo de daño refractario", "Reducir combustible"))
    if exceso_aire > 15:
        riesgos.append(("🟡", "Exceso de aire alto", "Enfriamiento excesivo", "Reducir aire de combustión"))
    if exceso_aire < 7:
        riesgos.append(("🔴", "Exceso de aire bajo", "Oxidación incompleta", "Aumentar aire"))
    if temp_cono < 650:
        riesgos.append(("🔴", "Cono inferior frío", "Riesgo alto de acumulación", "Revisar quemadores inferiores"))
    
    if not riesgos:
        st.success("✅ Operación dentro de parámetros recomendados")
    else:
        for emoji, titulo, desc, reco in riesgos:
            st.error(f"{emoji} **{titulo}**\n{desc}\n**Recomendación:** {reco}")

with tab3:
    st.subheader("Recomendaciones Generales")
    st.info("Ajustes recomendados según condiciones actuales:")
    st.markdown(f"""
    - **SMD ideal:** entre 80-150 µm  
    - **Temperatura quemadores:** 740-820 °C  
    - **Exceso de aire:** 8-14%  
    - **Temp. cono:** > 680 °C
    """)
    
    if st.button("Generar Reporte"):
        reporte = f"""Reporte Spray Roaster - {datetime.now().strftime("%Y-%m-%d %H:%M")}
Caudal total: {caudal_total} l/min
SMD: {smd:.0f} µm
Temp Quemadores: {temp_quemadores} °C
Temp Cono: {temp_cono} °C
Exceso aire: {exceso_aire:.1f} %

Recomendaciones: Ver sección de riesgos.
"""
        st.download_button("⬇️ Descargar Reporte", reporte, file_name="reporte_spray_roaster.txt")

with tab4:
    st.subheader("Notas Técnicas y Reglas")
    st.markdown("""
    **Reglas principales usadas:**
    - SMD ≈ 1750 × √(diámetro) / √(presión) × factor_temp
    - Gota ideal: 80-150 µm
    - Temperatura óptima quemadores: 740-820 °C
    - Exceso de aire recomendado: 8-14%
    - Evitar formación de magnetita (temp muy alta + gota fina)
    - Evitar óxido húmedo (gota grande + temp baja en cono)
    """)

st.caption("Herramienta desarrollada para mantenimiento - Ternium San Nicolás")
