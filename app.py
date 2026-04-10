import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESPLAZAMIENTO DE IDENTIDAD ---
def transmutador_identidad_torres(audio_data, delta_phi, rate):
    n_samples = len(audio_data)
    # Ventana de 80ms para conservar el timbre del piano de Bach
    grain_size = int(rate * 0.08) 
    step_size = int(grain_size * 0.4) # Mayor traslape para fluidez humana
    
    output = np.zeros(n_samples + grain_size)
    
    for i in range(0, n_samples - grain_size, step_size):
        # El desplazamiento de fase se aplica sobre el tiempo original
        # Esto calcula la "distancia" entre Bach y Elisa
        t_actual = i / n_samples
        fase_desplazada = (t_actual * delta_phi) % 1.0
        
        idx_bach = int(fase_desplazada * (n_samples - grain_size))
        
        grano = audio_data[idx_bach : idx_bach + grain_size].astype(np.float32)
        
        # Envolvente suave para evitar el sonido de "emulador"
        ventana = np.hamming(grain_size)
        output[i : i + grain_size] += grano * ventana

    # Normalización final
    output = (output / np.max(np.abs(output)) * 32767).astype(np.int16)
    return output

# --- INTERFAZ ---
st.title("🛡️ Sistema de Transmutación de Identidad")
st.write("Calculando el diferencial desde $M_0$ (Bach) hacia $M_{0b}$ (Elisa)")

# Usamos el diferencial de intervalo tonal (Sol -> La)
delta_phi = st.sidebar.number_input(
    "Diferencial de Desfase Real (Sol a La)", 
    format="%.15f", 
    value=1.122462048309373, 
    step=1e-15
)

archivo = st.file_uploader("Subir Bach Variaciones 1 (.wav)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Sintonizar Identidad"):
        resultado = transmutador_identidad_torres(data, delta_phi, rate)
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, resultado)
        st.audio(buffer, format='audio/wav')
