import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE GENOMA MUSICAL v38 ---
def motor_genoma_torres(delta_phi, rate):
    duracion = 8
    n_samples = int(rate * duracion)
    
    # EL SUSTRATO DE ADN (M0): Dos genomas distintos en la misma matriz
    # Genoma 0: Beethoven (Lírico/Salto de semitono)
    # Genoma 1: Williams (Marcial/Salto de cuarta)
    genomas = {
        "beethoven": [659.25, 622.25, 659.25, 622.25, 659.25, 493.88, 587.33, 523.25, 440.00],
        "williams": [196.00, 196.00, 196.00, 155.56, 233.08, 196.00, 155.56, 233.08, 196.00]
    }
    
    # LA REGLA DE SINTONIZACIÓN:
    # Si delta_phi está cerca de 1.0 -> Genoma Beethoven
    # Si delta_phi está cerca de 2.0 -> Genoma Williams
    if 0.5 <= delta_phi < 1.5:
        adn_activo = genomas["beethoven"]
        target = 1.0 # El centro de sintonía para Elisa
    else:
        adn_activo = genomas["williams"]
        target = 2.0 # El centro de sintonía para la Marcha
    
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # Calculamos la desviación (Qué tan lejos estamos del centro de sintonía)
    desviacion = abs(delta_phi - target)
    
    for i in range(n_samples):
        t = i / rate
        
        # El trayector Ñ recorre el genoma activo
        # La velocidad depende de la desviación: si te alejas del centro, se acelera (efecto Mario)
        paso = t * 6 * (1 + desviacion)
        indice = int(np.floor(paso)) % len(adn_activo)
        
        frecuencia = adn_activo[indice]
        
        # Generación de Onda Cuadrada (Nokia Style)
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        # El silencio de Nokia (puerta de ruido)
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        if (paso % 1.0) > 0.85: 
            muestra = 0
            
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v38: Selector de Genoma")
st.write("Sintoniza la identidad cambiando el diferencial ΔΦ.")

# Prueba con 1.0 para Beethoven o 2.0 para la Marcha
delta_phi = st.number_input("Introduce ΔΦ (Sintonizador)", value=1.0, format="%.2f")

if st.button("Sintonizar Identidad"):
    rate = 22050
    audio_data = motor_genoma_torres(delta_phi, rate)
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, audio_data)
    st.audio(buffer, format='audio/wav')
