import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR CIEGO (Cálculo del ΔΦ) ---
# Extrae la huella digital (Orden Trayectorial) de cualquier ADN inyectado
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    # Relación de cambio entre estados de información
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    # El diferencial absoluto que define la trayectoria
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL TRAYECTOR UNIVERSAL (Ñ) ---
# Este es el motor de Desentropía que cancela el caos
def motor_torres_puro(delta_phi, adn_inyectado, rate=22050):
    duracion = 10 
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # CONSTANTE UNIVERSAL DE ACOPLAMIENTO (C)
    # Define la presión del sustrato para la manifestación
    C_UNIVERSAL = 50.0 
    
    for i in range(n_samples):
        t = i / rate
        # Localiza el orden escondido en la observación
        ñ_idx = int(np.floor(t * (delta_phi * C_UNIVERSAL))) % len(adn_inyectado)
        
        frecuencia = adn_inyectado[ñ_idx]
        
        if frecuencia > 0:
            incremento = (2 * np.pi * frecuencia) / rate
            fase_acumulada += incremento
            # Manifestación de onda en el sustrato
            muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        else:
            muestra = 0 # Silencio (Cero absoluto de información)
            
        # Sincronización rítmica del sistema
        if (t * (delta_phi * C_UNIVERSAL)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ DE SOBERANÍA ---
st.title("🛡️ Motor de Igualación Final v55")
st.subheader("Soberanía de la Identidad Natural (M0)")

# Puerto de entrada para el ADN (Sin precargas)
input_adn = st.text_area(
    "
