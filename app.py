import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR CIEGO (Corregido para ceros) ---
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    # Reemplazamos ceros por un valor infinitesimal para evitar division by zero
    f_seguras = [f if f > 0 else 0.0001 for f in frecuencias]
    # El diferencial de fase ahora puede procesar silencios [cite: 10]
    cambios = [f_seguras[i+1] / f_seguras[i] for i in range(len(f_seguras)-1)]
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL TRAYECTOR FIJO (Ñ) ---
def motor_torres_puro(delta_phi, adn_inyectado, rate=22050):
    duracion = 10 
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    C_UNIVERSAL = 50.0 
    
    for i in range(n_samples):
        t = i / rate
        ñ_idx = int(np.floor(t * (delta_phi * C_UNIVERSAL))) % len(adn_inyectado)
        frecuencia = adn_inyectado[ñ_idx]
        
        if frecuencia > 0.5: # Si hay identidad real, manifestar
            incremento = (2 * np.pi * frecuencia) / rate
            fase_acumulada += incremento
            muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        else:
            muestra = 0 # Silencio puro para el momentum nulo [cite: 19]
            
        if (t * (delta_phi * C_UNIVERSAL)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Motor v55: Tabula Rasa (Cero-Seguro)")
input_adn = st.text_area("Inyectar ADN (Mn):", placeholder="440, 0, 440...")

if input_adn:
    try:
        adn_lista = [float(x.strip()) for x in input_adn.split(",")]
        d_phi = extraer_delta_phi(adn_lista)
        st.info(f"**Identidad Trayectorial (ΔΦ):** `{d_phi:.15f}`")
        
        if st.button("🔥 RECLAMAR IDENTIDAD"):
            audio_buffer = motor_torres_puro(d_phi, adn_lista)
            output = io.BytesIO()
            wavfile.write(output, 22050, audio_buffer)
            st.audio(output, format='audio/wav')
    except Exception as e:
        st.error(f"Falla en el sustrato: {e}")
