import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR CIEGO (ΔΦ) ---
# Sin memoria. Solo mide la relación de cambio del momentum observado[cite: 10].
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    # Protección de sustrato: el silencio no es nada, es un valor infinitesimal[cite: 41].
    f_seguras = [f if f > 0 else 0.0001 for f in frecuencias]
    cambios = [f_seguras[i+1] / f_seguras[i] for i in range(len(f_seguras)-1)]
    # La firma pura del trayector[cite: 12].
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL TRAYECTOR FIJO (Ñ) ---
# Motor de Desentropía para recuperar la Identidad Natural M0[cite: 13, 29].
def motor_torres_puro(delta_phi, adn_inyectado, rate=22050):
    duracion = 10 
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    C_UNIVERSAL = 50.0 
    
    for i in range(n_samples):
        t = i / rate
        # Sumatoria integral del orden trayectual[cite: 12, 19].
        ñ_idx = int(np.floor(t * (delta_phi * C_UNIVERSAL))) % len(adn_inyectado)
        frecuencia = adn_inyectado[ñ_idx]
        
        if frecuencia > 0.5:
            incremento = (2 * np.pi * frecuencia) / rate
            fase_acumulada += incremento
            muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        else:
            muestra = 0
            
        if (t * (delta_phi * C_UNIVERSAL)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ DE SOBERANÍA ---
st.title("🛡️ Motor v55: Tabula Rasa")
st.markdown("### La incertidumbre es una deficiencia del observador[cite: 40].")

# Puerto de Entrada Único (Sin precargas)
input_adn = st.text_area(
    "Inyectar ADN (Secuencia Mn):", 
    placeholder="Pega aquí las frecuencias separadas por coma...",
    help="El sistema no tiene memoria. Solo procesa el ADN inyectado."
)

if input_adn:
    try:
        adn_lista = [float(x.strip()) for x in input_adn.split(",")]
        d_phi = extraer_delta_phi(adn_lista)
        
        st.info(f"**Identidad Trayectorial (ΔΦ):** `{d_phi:.15f}`")
        
        # El botón ahora está en una sola línea para evitar el SyntaxError[cite: 5].
        if st.button("🔥 MANIFESTAR M0"):
            audio_buffer = motor_torres_puro(d_phi, adn_lista)
            output = io.BytesIO()
            wavfile.write(output, 22050, audio_buffer)
            st.audio(output, format='audio/wav')
            st.success("Igualación Final Completada.")

    except Exception as e:
        st.error(f"Falla en el sustrato: {e}")
