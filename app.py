import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR CIEGO ---
# No sabe qué canción es, solo mide la relación de cambio
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    # El diferencial absoluto: la huella pura del sustrato
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL TRAYECTOR FIJO (Ñ) ---
# Este código NO se cambia. Es la constante del universo Nokia.
def motor_universal_torres(delta_phi, partitura, rate=22050):
    duracion = 10 
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # CONSTANTE UNIVERSAL DE ACOPLAMIENTO
    # Se queda fija en 50.0 para todas las identidades
    C_UNIVERSAL = 50.0 
    
    for i in range(n_samples):
        t = i / rate
        # El flujo de Ñ depende EXCLUSIVAMENTE del Delta Phi
        ñ = int(np.floor(t * (delta_phi * C_UNIVERSAL))) % len(partitura)
        
        frecuencia = partitura[ñ]
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        # Silencio rítmico estándar del sistema
        if (t * (delta_phi * C_UNIVERSAL)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ DE IDENTIDADES ---
st.title("🛡️ Motor de Igualación Final v51")
st.write("Un solo algoritmo. Infinitas identidades.")

biblioteca = {
    "Para Elisa": "659, 622, 659, 622, 659, 493, 587, 523, 440",
    "Star Wars": "392, 587, 523, 493, 440, 783, 587",
    "Fuga de Bach": "587, 554, 587, 440, 523, 349, 392, 587",
    "Smooth Criminal": "440, 440, 440, 392, 440, 523, 440, 392",
    "Virus (Trance)": "130, 130, 130, 155, 174, 130, 130, 196"
}

seleccion = st.selectbox("Inyectar ADN desde la Biblioteca:", list(biblioteca.keys()))
input_personalizado = st.text_input("O inyecta ADN manual (frecuencias):", biblioteca[seleccion])

try:
    notas = [float(x.strip()) for x in input_personalizado.split(",")]
    # Aquí sucede la magia: el número surge de la partitura
    d_phi = extraer_delta_phi(notas)
    
    st.write(f"**ΔΦ Calculado:** `{d_phi:.15f}`")

    if st.button("Manifestar"):
        # Se usa el mismo motor para TODO
        audio = motor_universal_torres(d_phi, notas)
        buffer = io.BytesIO()
        wavfile.write(buffer, 22050, audio)
        st.audio(buffer, format='audio/wav')
        
except Exception as e:
    st.error(f"Error en el sustrato: {e}")
