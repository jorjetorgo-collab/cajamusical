import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR (ADN) ---
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    # Limpiamos ceros para no romper la división
    f_limpias = [f if f > 0 else 0.1 for f in frecuencias]
    cambios = [f_limpias[i+1] / f_limpias[i] for i in range(len(f_limpias)-1)]
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL MOTOR (SUSTRATO) ---
def motor_universal(delta_phi, partitura, constante_c, rate=22050):
    duracion = 10 
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    for i in range(n_samples):
        t = i / rate
        # Ñ ahora obedece al Slider de la interfaz
        ñ = int(np.floor(t * (delta_phi * constante_c))) % len(partitura)
        
        frecuencia = partitura[ñ]
        if frecuencia > 0.5: # Si no es un "silencio"
            incremento = (2 * np.pi * frecuencia) / rate
            fase_acumulada += incremento
            muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        else:
            muestra = 0
            
        # Pulso rítmico
        if (t * (delta_phi * constante_c)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- 3. INTERFAZ (LA CONSOLA) ---
st.title("🛡️ Motor v53: Control de Presión")

# AQUÍ ESTÁ LO QUE FALTABA: El control de velocidad
c_usuario = st.slider("Ajuste de Presión (C):", min_value=5.0, max_value=150.0, value=40.0)

biblioteca = {
    "Pantera Rosa": "138, 146, 0, 155, 164, 0, 138, 146, 155, 164, 207, 196",
    "Star Wars": "392, 587, 523, 493, 440, 783, 587",
    "Misión Imposible": "392, 392, 466, 523, 392, 392, 349, 370"
}

seleccion = st.selectbox("Elegir Genoma:", list(biblioteca.keys()))
input_notas = st.text_input("ADN (Frecuencias):", biblioteca[seleccion])

try:
    notas = [float(x.strip()) for x in input_notas.split(",")]
    d_phi = extraer_delta_phi(notas)
    
    st.write(f"**ΔΦ (Identidad):** `{d_phi:.10f}`")
    st.write(f"**Velocidad Actual:** `{d_phi * c_usuario:.2f} notas/seg`")

    if st.button("Manifestar en el Sustrato"):
        audio = motor_universal(d_phi, notas, c_usuario)
        buffer = io.BytesIO()
        wavfile.write(buffer, 22050, audio)
        st.audio(buffer, format='audio/wav')
        
except:
    st.error("Error en los datos")
