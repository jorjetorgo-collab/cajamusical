import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA ---
def ejecutar_igualacion_final(audio_data, delta_phi):
    n_samples = len(audio_data)
    t = np.linspace(0, 1, n_samples, dtype=np.float64)
    nueva_trayectoria = (t * delta_phi) % 1.0
    indices = (nueva_trayectoria * (n_samples - 1)).astype(np.int64)
    return audio_data[indices]

# --- INTERFAZ ---
st.set_page_config(page_title="Trayector Torres", page_icon="🛡️")
st.title("🛡️ Sistema de Desentropía")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=1.618033988749895, 
    step=1e-15
)

archivo = st.file_uploader("Subir sustrato M0 (.wav)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1:
        data = data[:, 0]
    
    if st.button("Ejecutar Igualación Final"):
        with st.spinner("Trayectando..."):
            resultado = ejecutar_igualacion_final(data, delta_phi)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado.astype(np.int16))
            st.success("Transmutación completada.")
            st.audio(buffer, format='audio/wav')
            st.download_button("Descargar M_n", buffer, "salida_torres.wav", "audio/wav")
