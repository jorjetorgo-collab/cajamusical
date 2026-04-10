import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EXTRACTOR DE ADN ---
def extraer_delta_phi(frecuencias):
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    return np.mean(cambios) * np.std(cambios)

# --- 2. TRAYECTOR CALIBRADO v42 ---
def motor_trayector_calibrado(delta_phi, partitura_base, rate):
    duracion = 8
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # CONSTANTE DE ACOPLAMIENTO (C)
    # Esta constante evita el efecto 'láser' al normalizar la presión de Ñ
    C = 45.0  # Factor de escala para llevar el 0.125 a un tempo de ~120 BPM
    
    for i in range(n_samples):
        t = i / rate
        # Ñ ahora fluye con la resistencia del sustrato
        # El diferencial dicta la 'curvatura', pero C dicta la 'velocidad'
        ñ = int(np.floor(t * (delta_phi * C))) % len(partitura_base)
        
        frecuencia = partitura_base[ñ]
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        # Onda cuadrada (Nokia)
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        
        # Silencio rítmico proporcional al diferencial
        if (t * (delta_phi * C)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v42: Descompresión de Identidad")
st.write("Calibrando el diferencial para evitar el colapso en láser.")

input_notas = st.text_input("Partitura", "659.25, 622.25, 659.25, 622.25, 659.25, 493.88, 587.33, 523.25, 440.0")
notas = [float(x.strip()) for x in input_notas.split(",")]

d_phi = extraer_delta_phi(notas)
st.write(f"**ΔΦ Extraído:** `{d_phi:.15f}`")

if st.button("Manifestar Melodía Descomprimida"):
    rate = 22050
    audio = motor_trayector_calibrado(d_phi, notas, rate)
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, audio)
    st.audio(buffer, format='audio/wav')
