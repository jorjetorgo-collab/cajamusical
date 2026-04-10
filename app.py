import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR CON INERCIA v50 ---
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 0.0
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    return np.mean(cambios) * np.std(cambios)

def motor_manifestador_lento(delta_phi, partitura, rate):
    duracion = 12 # Le damos más tiempo para respirar
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # Bajamos la constante C para frenar la 'verguiza'
    # Pasamos de 100.0 a 40.0 para que sea solemne
    C = 40.0 
    
    for i in range(n_samples):
        t = i / rate
        # Ñ ahora camina, no corre
        ñ = int(np.floor(t * (delta_phi * C))) % len(partitura)
        
        frecuencia = partitura[ñ]
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        
        # Silencio rítmico elegante
        if (t * (delta_phi * C)) % 1.0 > 0.85: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v50: La Fuga Solemne")
st.write("Frenando la inercia del ΔΦ para recuperar la elegancia.")

fuga_notas = "587.33, 554.37, 587.33, 440.00, 523.25, 349.23, 392.00, 587.33"
d_phi = extraer_delta_phi([float(x) for x in fuga_notas.split(",")])

if st.button("Manifestar con Inercia (Lento)"):
    audio = motor_manifestador_lento(d_phi, [float(x) for x in fuga_notas.split(",")], 22050)
    buffer = io.BytesIO()
    wavfile.write(buffer, 22050, audio)
    st.audio(buffer, format='audio/wav')
