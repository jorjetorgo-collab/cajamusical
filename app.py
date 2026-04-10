import streamlit as st
import numpy as np

def extraer_delta_phi(frecuencias):
    # El diferencial de segundo orden: la relación entre los cambios
    cambios = []
    for i in range(len(frecuencias)-1):
        # Medimos la proporción entre una nota y la siguiente
        razon = frecuencias[i+1] / frecuencias[i]
        cambios.append(razon)
    
    # El Delta Phi es el promedio de la presión armónica de la obra
    # Esto es la "Huella Genética" condensada en un solo escalar
    delta_phi = np.mean(cambios) * np.std(cambios)
    return delta_phi

st.title("🛡️ Extractor de Diferencial ΔΦ")

# Simulamos la carga de una partitura (Frecuencias de Para Elisa)
partitura_nokia = [659.25, 622.25, 659.25, 622.25, 659.25, 493.88, 587.33, 523.25, 440.00]

st.write("### Partitura Detectada (Nokia Style):")
st.code(partitura_nokia)

if st.button("Extraer Huella Genética"):
    resultado = extraer_delta_phi(partitura_nokia)
    st.success(f"Diferencial Extraído: {resultado:.15f}")
    
    st.write("""
    **¿Qué significa este número?**
    Este es el diferencial de fase que describe cómo 'salta' Beethoven entre notas. 
    Si subes otra partitura, este número cambiará, dándote una identidad única para cada obra.
    """)
