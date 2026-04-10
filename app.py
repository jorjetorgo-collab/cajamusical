import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR ROBUSTO v44 ---
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2:
        return 0.0
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    return np.mean(cambios) * np.std(cambios)

def motor_manifestador(delta_phi, partitura, rate):
    if delta_phi == 0 or not partitura:
        return np.zeros(100).astype(np.uint8)
    
    duracion = 6
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    # Si el delta es muy bajo, compensamos para que no sea un láser
    C = 60.0 if delta_phi > 0.05 else 200.0 
    
    for i in range(n_samples):
        t = i / rate
        ñ = int(np.floor(t * (delta_phi * C))) % len(partitura)
        
        frecuencia = partitura[ñ]
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        if (t * (delta_phi * C)) % 1.0 > 0.7: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v44: Modo Libre")

opcion = st.selectbox("Selecciona un Genoma:", 
                     ["Smooth Criminal", "Para Elisa", "Personalizada"])

if opcion == "Smooth Criminal":
    raw_notas = "440, 440, 440, 392, 440, 523, 440, 392"
elif opcion == "Para Elisa":
    raw_notas = "659, 622, 659, 622, 659, 493, 587, 523"
else:
    # Ponemos una melodía de ejemplo (Do-Re-Mi) para que no esté vacío al inicio
    raw_notas = st.text_input("Escribe frecuencias separadas por coma:", "261.63, 293.66, 329.63, 349.23")

# Validación para evitar el error de ValueError
if raw_notas.strip() == "":
    st.warning("Por favor, introduce al menos dos frecuencias para calcular el ADN.")
else:
    try:
        notas = [float(x.strip()) for x in raw_notas.split(",") if x.strip() != ""]
        
        if len(notas) < 2:
            st.info("Necesito al menos 2 notas para ver el 'salto' entre ellas.")
        else:
            d_phi = extraer_delta_phi(notas)
            st.write(f"**Identidad Única (ΔΦ):** `{d_phi:.15f}`")

            if st.button("Manifestar Sonido"):
                audio = motor_manifestador(d_phi, notas, 22050)
                buffer = io.BytesIO()
                wavfile.write(buffer, 22050, audio)
                st.audio(buffer, format='audio/wav')
    except ValueError:
        st.error("Error: Asegúrate de usar solo números y comas (ejemplo: 440, 880, 220).")
