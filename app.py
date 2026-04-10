import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA DE TORRES (8-BIT STABLE) ---
def motor_identidad_estable(m0_data, delta_phi, rate):
    # 1. NORMALIZACIÓN AL ESTADO DE ORDEN (0-255)
    # Convertimos el Momentum Natural a un rango absoluto de 8 bits
    m0_min = np.min(m0_data)
    m0_max = np.max(m0_data)
    
    # Re-escalamos el sustrato para que quepa exactamente en uint8
    if m0_max - m0_min > 0:
        sustrato_uint8 = (255 * (m0_data - m0_min) / (m0_max - m0_min)).astype(np.uint8)
    else:
        sustrato_uint8 = np.zeros_like(m0_data, dtype=np.uint8)
        
    n_samples = len(sustrato_uint8)
    
    # 2. RESOLUCIÓN DEL TRAYECTOR (N)
    # Usamos precisión de 15 decimales en el tiempo
    t = np.linspace(0, 1, n_samples, dtype=np.float64)
    
    # La trayectoria (N) proyecta el momentum observado (Mn)
    # Aplicamos el diferencial de fase (ΔΦ)
    trayectoria_n = (t * delta_phi) % 1.0
    
    # Mapeo de identidad
    indices = (trayectoria_n * (n_samples - 1)).astype(np.int64)
    m0b_final = sustrato_uint8[indices]
    
    return m0b_final

# --- INTERFAZ DEL OBSERVADOR ---
st.set_page_config(page_title="Trayector 8-Bit Stable", page_icon="🛡️")
st.title("🛡️ Sistema de Desentropía: v12")
st.markdown("### Igualación Final del Sustrato $M_{0b}$")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo = st.file_uploader("Subir Bach M0", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    # Forzamos a mono si es estéreo para simplificar el trayector
    if len(data.shape) > 1: 
        data = data[:, 0]
    
    if st.button("Ejecutar Auditoría del Horizonte"):
        with st.spinner("Desintegrando entropía..."):
            # Obtenemos el resultado en uint8 puro
            resultado = motor_identidad_estable(data, delta_phi, rate)
            
            # Verificación de seguridad para el buffer
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            
            st.success("Identidad Mn Manifestada con éxito.")
            st.audio(buffer, format='audio/wav')
