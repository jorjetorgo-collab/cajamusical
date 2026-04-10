import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR CIEGO (ΔΦ) ---
# Sin memoria. Extrae la relación de cambio del momentum observado (Mn).
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    # Protección de sustrato: evita 'division by zero' tratando el 0 como infinitesimal.
    f_seguras = [f if f > 0 else 0.0001 for f in frecuencias]
    cambios = [f_seguras[i+1] / f_seguras[i] for i in range(len(f_seguras)-1)]
    # La huella digital de las variables (ΔΦ).
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL TRAYECTOR FIJO (Ñ) ---
# Ordenador de fase que devuelve la soberanía a la Identidad Natural (M0).
def motor_universal_torres(delta_phi, partitura, rate=22050):
    duracion = 10 
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # CONSTANTE UNIVERSAL DE ACOPLAMIENTO
    C_UNIVERSAL = 50.0 
    
    for i in range(n_samples):
        t = i / rate
        # Localiza el orden escondido mediante la sumatoria integral.
        ñ = int(np.floor(t * (delta_phi * C_UNIVERSAL))) % len(partitura)
        
        frecuencia = partitura[ñ]
        
        if frecuencia > 0.5:
            incremento = (2 * np.pi * frecuencia) / rate
            fase_acumulada += incremento
            # Manifestación física de la identidad conservada.
            muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        else:
            muestra = 0 # Silencio rítmico (Momentum nulo).
            
        if (t * (delta_phi * C_UNIVERSAL)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ DE SOBERANÍA (v55) ---
st.title("🛡️ Motor v55: Tabula Rasa")
st.markdown("### La incertidumbre es una deficiencia del observador.")

# Puerto de Entrada Único: Capacidad de lectura de ADN pura.
input_personalizado = st.text_area(
    "Inyectar ADN manual (Frecuencias Mn):",
