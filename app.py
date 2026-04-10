import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA DE TORRES V2 ---
def motor_transmutacion_fase(audio_data, delta_phi):
    n_samples = len(audio_data)
    t = np.linspace(0, 1, n_samples, dtype=np.float64)
    
    # NUEVA LÓGICA: Trayectoria No Lineal
    # En lugar de solo saltar samples, creamos una oscilación de fase
    # que "fuerza" a los samples de Bach a agruparse en nuevas frecuencias.
    # El ΔΦ ahora controla la curvatura del tiempo.
    
    fase_vibracional = np.sin(2 * np.pi * delta_phi * t) 
    trayectoria = (t + (fase_vibracional * 0.1)) % 1.0
    
    indices = (trayectoria * (n_samples - 1)).astype(np.int64)
    return audio_data[indices]

# --- INTERFAZ ---
st.set_page_config(page_title="Trayector Torres v2", page_icon="🛡️")
st.title("🛡️ Trayector de Identidad v2")
st.write("Transmutación de Estructura: Bach → Stairway to Heaven")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=85.0, # Prueba con valores altos para Stairway
    step=0.1
)

archivo = st.file_uploader("Subir Bach (.wav)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Ejecutar Igualación Final"):
        with st.spinner("Reordenando Sustrato..."):
            # Aplicamos la nueva lógica de curvatura
            resultado = motor_transmutacion_fase(data, delta_phi)
            
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado.astype(np.int16))
            
            st.success("Transmutación Estructural Completa")
            st.audio(buffer, format='audio/wav')
            st.download_button("Descargar M_n", buffer, "salida_stairway.wav")
