import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE CUANTIZACIÓN DE IDENTIDAD (TORRES v10) ---
def motor_cuantizado_m0b(m0_data, delta_phi, rate):
    # 1. ALTA RESOLUCIÓN: 64-bit para precisión total del Delta Phi
    m0_64 = m0_data.astype(np.float64) / 32768.0
    n_samples = len(m0_64)
    
    # 2. DEFINICIÓN DE LA REJILLA (Tempo de Para Elisa)
    bpm = 120 
    samples_per_beat = int(rate * (60 / bpm) * 0.25) # Semicorcheas
    m0b_final = np.zeros(n_samples + samples_per_beat)
    
    # 3. ENSAMBLAJE POR PULSOS
    for i in range(0, n_samples - samples_per_beat, samples_per_beat):
        # El ΔΦ ahora decide qué "celda" de Bach corresponde a esta celda de Beethoven
        t = i / n_samples
        
        # Trayectoria de Identidad: Buscamos la coincidencia rítmica
        desfase_identidad = (np.sin(t * delta_phi) * 0.5 + 0.5)
        idx_origen = int(desfase_identidad * (n_samples - samples_per_beat))
        
        # Extraemos el "átomo" de piano
        atomo = m0_64[idx_origen : idx_origen + samples_per_beat]
        
        # Aplicamos envolvente de percusión (Piano Attack)
        # Esto quita el sonido de "trastes" y da el golpe de la tecla
        ventana = np.exp(-np.linspace(0, 5, len(atomo))) 
        
        m0b_final[i : i + samples_per_beat] += atomo * ventana

    # 4. NORMALIZACIÓN Y SALIDA
    m0b_final = m0b_final / (np.max(np.abs(m0b_final)) + 1e-9)
    return (m0b_final * 32767).astype(np.int16)

# --- INTERFAZ ---
st.title("🛡️ Trayector v10: Cuantización de Identidad")
st.write("Alineando el sustrato de Bach a la rejilla temporal de Beethoven.")

delta_phi = st.sidebar.number_input(
    "Diferencial de Rejilla", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo = st.file_uploader("Subir Bach M0", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Cuantizar y Transmutar"):
        with st.spinner("Sincronizando fases armónicas..."):
            resultado = motor_cuantizado_m0b(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("M0b sintonizado a la rejilla.")
            st.audio(buffer, format='audio/wav')
