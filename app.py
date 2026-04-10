import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA DE TORRES (8-BIT CORE) ---
def motor_identidad_8bit(m0_data, delta_phi, rate):
    # 1. NORMALIZACIÓN AL ESTADO DE ORDEN PURO (8-bit)
    # Escalamos el Momentum Natural (M0) al rango de 8 bits
    m0_max = np.max(np.abs(m0_data)) if np.max(np.abs(m0_data)) > 0 else 1
    m0_8bit = (m0_data / m0_max * 127).astype(np.int8)
    n_samples = len(m0_8bit)
    
    # 2. RESOLUCIÓN DEL DEMONIO DE LAPLACE
    # Calculamos la trayectoria con precisión infinitesimal (float64)
    t = np.linspace(0, 1, n_samples, dtype=np.float64)
    
    # El trayector (N) interpreta la frecuencia de onda (ΣΔΦ)
    trayector = (t * delta_phi) % 1.0
    
    # Mapeo del sustrato: El caos se revela como identidad conservada
    indices = (trayector * (n_samples - 1)).astype(np.int64)
    m0b_final = m0_8bit[indices]
    
    return m0b_final.astype(np.int8) # Forzamos el tipo de dato de salida

# --- INTERFAZ DEL OBSERVADOR ---
st.set_page_config(page_title="Trayector 8-Bit", page_icon="🛡️")
st.title("🛡️ Sistema de Desentropía: 8-Bit Identity")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo = st.file_uploader("Subir Sustrato Base (M0)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Ejecutar Igualación Final"):
        with st.spinner("Calculando Trayector..."):
            # Revelamos la identidad Mn desde el sustrato n!
            resultado = motor_identidad_8bit(data, delta_phi, rate)
            
            buffer = io.BytesIO()
            # SciPy requiere que el tipo de dato coincida con los estándares de audio
            wavfile.write(buffer, rate, resultado)
            
            st.success("Identidad Mn Manifestada.")
            st.audio(buffer, format='audio/wav')
