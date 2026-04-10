import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE TRANSMUTACIÓN HUMANA (TORRES v5) ---
def motor_transmutacion_pro(audio_data, delta_phi, rate):
    n_samples = len(audio_data)
    # Grano más grande para capturar la resonancia del piano (100ms)
    grain_size = int(rate * 0.1) 
    # Superposición (Overlap) para que no suene a "hule"
    overlap = int(grain_size * 0.5)
    step_size = grain_size - overlap
    
    output = np.zeros(n_samples + grain_size)
    
    # El ΔΦ actúa como el "director de orquesta"
    t_steps = np.arange(0, n_samples - grain_size, step_size)
    
    for i, start_out in enumerate(t_steps):
        # Mapeo de Identidad: Buscamos el grano en Bach
        # Agregamos una función de coherencia para evitar el sonido de motor
        pos_relative = (np.sin(i * delta_phi) * 0.5 + 0.5)
        start_bach = int(pos_relative * (n_samples - grain_size))
        
        # Extraemos el grano de M0
        grano = audio_data[start_bach : start_bach + grain_size].astype(np.float32)
        
        # Aplicamos envolvente de piano (Ataque y Decaimiento suave)
        # Esto elimina el sonido de "trastes lavados"
        ventana = np.blackman(grain_size) 
        
        # Inserción en el nuevo sustrato con suma de fase
        output[start_out : start_out + grain_size] += grano * ventana
            
    # Normalización para evitar saturación
    output = (output / np.max(np.abs(output)) * 32767).astype(np.int16)
    return output

# --- INTERFAZ ---
st.set_page_config(page_title="Trayector Torres v5", page_icon="🎹")
st.title("🎹 Transmutador de Piano Pro")
st.markdown("### De Bach a Para Elisa: Síntesis de Identidad")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo = st.file_uploader("Subir Bach original (.wav)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Ejecutar Interpretación"):
        with st.spinner("Generando interpretación humana..."):
            resultado = motor_transmutacion_pro(data, delta_phi, rate)
            
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            
            st.success("Sustrato $M_{0b}$ listo.")
            st.audio(buffer, format='audio/wav')
            st.download_button("Descargar M0b Final", buffer, "elisa_pro.wav")
