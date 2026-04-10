import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- GENERADOR DE ESCALA CROMÁTICA CONTINUA ---
def generar_sustrato_fluido(rate):
    # Generamos las 12 notas de la octava central
    frecuencias = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 
                   369.99, 392.00, 415.30, 440.00, 466.16, 493.88]
    muestras_por_nota = int(rate * 0.1) # Notas muy cortas para mayor densidad
    sustrato = np.array([])
    
    for f in frecuencias:
        t = np.linspace(0, 0.1, muestras_por_nota, endpoint=False)
        # Onda cuadrada (Nokia 8-bit)
        nota = np.sign(np.sin(2 * np.pi * f * t))
        sustrato = np.append(sustrato, nota)
    return sustrato

# --- MOTOR TRAYECTOR v23 ---
def motor_torres_fluido(delta_phi, rate):
    sustrato = generar_sustrato_fluido(rate)
    n_samples_lib = len(sustrato)
    
    duracion_out = 10
    n_samples_out = int(rate * duracion_out)
    resultado_mn = np.zeros(n_samples_out)
    
    t = np.arange(n_samples_out) / rate
    
    # EL AJUSTE MAESTRO: 
    # Usamos una función seno basada en Delta Phi para que el trayector 
    # "baile" sobre la escala cromática de forma constante.
    # Esto garantiza que SIEMPRE haya sonido.
    indices = ((np.sin(t * delta_phi) + 1) / 2 * (n_samples_lib - 1))
    
    for i in range(n_samples_out):
        idx = int(indices[i])
        resultado_mn[i] = sustrato[idx]
        
    # Normalización y salida 8-bit
    mn_max = np.max(np.abs(resultado_mn)) if np.max(np.abs(resultado_mn)) > 0 else 1
    return (127 * (resultado_mn / mn_max) + 128).astype(np.uint8)

# --- INTERFAZ ---
st.set_page_config(page_title="🛡️ Torres v23 - Oscilador", page_icon="🌊")
st.title("🛡️ Trayector v23: Oscilación de Identidad")
st.write("Sintonizando la escala cromática pura mediante el diferencial de fase.")

delta_phi = st.sidebar.number_input(
    "ΔΦ (Frecuencia de Identidad)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

rate = 22050

if st.button("Generar Sonido de Identidad"):
    with st.spinner("Haciendo vibrar el sustrato..."):
        resultado = motor_torres_fluido(delta_phi, rate)
        
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, resultado)
        
        st.success("Trayectoria sintonizada.")
        st.audio(buffer, format='audio/wav')
