import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR (Encuentra el ADN) ---
def extraer_delta_phi(frecuencias):
    # Medimos la 'curvatura' armónica de la melodía
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    # El Delta Phi es la firma de esa fluctuación
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL TRAYECTOR (Usa el ADN para crear sonido) ---
def motor_trayector_ñ(delta_phi, partitura_base, rate):
    duracion = 8
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # El sustrato se calibra con el Delta Phi
    # Ñ es el integrador que sabe cuándo saltar de nota
    for i in range(n_samples):
        t = i / rate
        # Ñ decide la posición en la melodía basándose en el diferencial
        ñ = int(np.floor(t * 6 / delta_phi)) % len(partitura_base)
        
        frecuencia = partitura_base[ñ]
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        # Onda cuadrada estilo Nokia
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        # Silencio rítmico
        if (t * 6 / delta_phi) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Sistema de Identidad Unificado v41")

# Puedes cambiar estos números (la partitura) y el Delta Phi se ajustará solo
input_notas = st.text_input("Partitura (Frecuencias separadas por coma)", 
                             "659.25, 622.25, 659.25, 622.25, 659.25, 493.88, 587.33, 523.25, 440.0")

notas = [float(x.strip()) for x in input_notas.split(",")]

# PASO 1: EXTRAER
d_phi = extraer_delta_phi(notas)
st.write(f"**ADN Extraído ($\Delta\Phi$):** `{d_phi:.15f}`")

# PASO 2: MANIFESTAR
if st.button("Manifestar Identidad desde ΔΦ"):
    rate = 22050
    audio = motor_trayector_ñ(d_phi, notas, rate)
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, audio)
    st.audio(buffer, format='audio/wav')
