import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE HUELLA GENÉTICA v36 ---
def motor_torres_genetico(delta_phi, rate):
    duracion = 12
    n_samples = int(rate * duracion)
    f_la = 440.0 
    
    resultado = np.zeros(n_samples)
    
    # Ñ es la suma acumulada de la huella genética
    N_tilde = 0.0
    fase_audio = 0.0
    
    for i in range(n_samples):
        t = i / rate
        
        # 1. EL DIFERENCIADOR (La esencia de tu idea)
        # Extraemos el diferencial del pulso y del tono desde delta_phi
        # Usamos la parte fraccionaria para que Ñ 'sienta' el cambio
        diferencial_tempo = (delta_phi * t) % 1.0
        diferencial_tono = (delta_phi / (t + 1)) % 1.0
        
        # 2. LA SUMA (Ñ como Huella Genética)
        # Ñ acumula el cambio de tempo y tono segundo a segundo
        cambio_instante = (diferencial_tempo + diferencial_tono) * delta_phi
        N_tilde += cambio_instante / rate 
        
        # 3. LA MANIFESTACIÓN (M0 -> Mn)
        # Ñ ahora dicta la frecuencia final de forma no lineal
        frecuencia = f_la * (1 + (N_tilde % 2.0))
        
        # Generación de la muestra (Onda de 8 bits)
        fase_audio += (2 * np.pi * frecuencia) / rate
        resultado[i] = np.sign(np.sin(fase_audio))
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v36: Integrador de Huella Genética")
st.write("Ñ aquí es la suma de los diferenciales de tiempo y tono.")

delta_phi = st.number_input("ΔΦ Maestro", format="%.15f", value=2.721055555555556)

if st.button("Calcular Huella Ñ"):
    rate = 22050
    audio_data = motor_torres_genetico(delta_phi, rate)
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, audio_data)
    st.audio(buffer, format='audio/wav')
