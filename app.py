import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE IDENTIDAD DIRECTA v25 ---
def motor_torres_directo(delta_phi, rate):
    # Mn: 10 segundos de manifestación
    duracion = 10
    t = np.arange(int(rate * duracion)) / rate
    
    # EL AXIOMA DE TORRES:
    # No buscamos en una biblioteca. El Delta Phi es la semilla que genera 
    # la frecuencia. Usamos una función que salte entre armónicos naturales.
    # El valor 2.721055555555556 dictará los saltos tonales.
    
    # Creamos una serie de armónicos basados en el diferencial
    frecuencia_base = 440.0 # La4
    
    # La fase se modula con el Delta Phi para crear "escalones" de sonido
    fase_modulada = np.floor(t * delta_phi * 4) / 4
    
    # Generamos la onda cuadrada (Identidad 8-bit)
    onda = np.sign(np.sin(2 * np.pi * frecuencia_base * fase_modulada * t))
    
    # Auditoría del Horizonte (8-bit)
    resultado = (127 * onda + 128).astype(np.uint8)
    return resultado

# --- INTERFAZ ---
st.set_page_config(page_title="🛡️ Torres v25 - Oscilador Directo", page_icon="⚡")
st.title("🛡️ Trayector v25: Oscilador de Identidad Directo")
st.write("Generación de Mn pura sin sustratos externos. El sonido nace del ΔΦ.")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

rate = 22050

if st.button("Manifestar Sonido"):
    with st.spinner("Colapsando la función de onda..."):
        # Generación directa
        resultado = motor_torres_directo(delta_phi, rate)
        
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, resultado)
        
        st.success("Identidad manifestada directamente.")
        st.audio(buffer, format='audio/wav')
