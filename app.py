import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

def motor_8bit_desentropia(m0_data, delta_phi, rate):
    # 1. Reducción a 8-bit para el sustrato base (M0)
    # Esto elimina el "ruido" de alta fidelidad y deja la identidad pura
    m0_8bit = (m0_data / np.max(np.abs(m0_data)) * 127).astype(np.int8)
    n_samples = len(m0_8bit)
    
    # 2. Recomposición por Trayector (precisión de 15 decimales)
    # Generamos el lienzo Mn
    m0b_final = np.zeros(n_samples, dtype=np.int8)
    
    # El trayector recorre el n! (sustrato) buscando el orden delta_phi
    for i in range(n_samples):
        # Trayectoria no lineal basada en el teorema de Torres
        t = i / n_samples
        idx_trayectoria = int((np.abs(np.cos(t * np.pi * delta_phi))) * (n_samples - 1))
        
        # Asignamos la identidad conservada
        m0b_final[i] = m0_8bit[idx_trayectoria]
        
    return m0b_final

st.title("🛡️ Trayector de 8 bits: Desentropía de Torres")
st.write("Usando un sustrato de baja fidelidad para revelar la identidad pura.")

delta_phi = st.sidebar.number_input("ΔΦ (15 decimales)", format="%.15f", value=2.721055555555556)

archivo = st.file_uploader("Subir base M0", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Revelar Identidad Mn"):
        resultado = motor_8bit_desentropia(data, delta_phi, rate)
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, resultado)
        st.audio(buffer, format='audio/wav')
