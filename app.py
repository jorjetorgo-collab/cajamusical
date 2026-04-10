import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR UNIVERSAL v43 ---
def extraer_delta_phi(frecuencias):
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    return np.mean(cambios) * np.std(cambios)

def motor_manifestador(delta_phi, partitura, rate):
    duracion = 6
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    C = 60.0 # Ajuste de tempo para esta huella
    
    for i in range(n_samples):
        t = i / rate
        # Ñ recorre el nuevo ADN
        ñ = int(np.floor(t * (delta_phi * C))) % len(partitura)
        
        frecuencia = partitura[ñ]
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        # Onda cuadrada Nokia
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        # Silencio más corto para que sea más rítmico
        if (t * (delta_phi * C)) % 1.0 > 0.7: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v43: Nuevas Identidades")

opcion = st.selectbox("Selecciona un Genoma Musical:", 
                     ["Smooth Criminal (Jackson)", "Para Elisa (Beethoven)", "Personalizada"])

if opcion == "Smooth Criminal (Jackson)":
    raw_notas = "440.0, 440.0, 440.0, 392.0, 440.0, 523.25, 440.0, 392.0, 349.23, 392.0, 349.23, 329.63"
elif opcion == "Para Elisa (Beethoven)":
    raw_notas = "659.25, 622.25, 659.25, 622.25, 659.25, 493.88, 587.33, 523.25, 440.0"
else:
    raw_notas = st.text_input("Escribe tus frecuencias:")

notas = [float(x.strip()) for x in raw_notas.split(",")]
d_phi = extraer_delta_phi(notas)

st.write(f"**Identidad Calculada (ΔΦ):** `{d_phi:.15f}`")

if st.button("Manifestar Sonido"):
    audio = motor_manifestador(d_phi, notas, 22050)
    buffer = io.BytesIO()
    wavfile.write(buffer, 22050, audio)
    st.audio(buffer, format='audio/wav')
