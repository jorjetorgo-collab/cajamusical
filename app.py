import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR CIEGO (ΔΦ) ---
# No conoce canciones. Extrae la huella del Momentum Observado (Mn).
# Implementa protección infinitesimal para evitar "division by zero".
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    # El sustrato trata el silencio (0) como una posibilidad física cercana al vacío
    f_seguras = [f if f > 0 else 0.0001 for f in frecuencias]
    # Diferencial de fase: la huella pura del orden trayectual
    cambios = [f_seguras[i+1] / f_seguras[i] for i in range(len(f_seguras)-1)]
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL TRAYECTOR FIJO (Ñ) ---
# Motor de Desentropía que devuelve la soberanía a la Identidad Natural (M0).
def motor_torres_puro(delta_phi, adn_inyectado, rate=22050):
    duracion = 10 
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # CONSTANTE UNIVERSAL DE ACOPLAMIENTO (C)
    C_UNIVERSAL = 50.0 
    
    for i in range(n_samples):
        t = i / rate
        # Localiza el orden escondido mediante la sumatoria integral del trayector
        ñ_idx = int(np.floor(t * (delta_phi * C_UNIVERSAL))) % len(adn_inyectado)
        
        frecuencia = adn_inyectado[ñ_idx]
        
        if frecuencia > 0.5: # Si hay identidad real, manifestar
            incremento = (2 * np.pi * frecuencia) / rate
            fase_acumulada += incremento
            # Manifestación física de la identidad conservada
            muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        else:
            muestra = 0 # Silencio absoluto (Momentum nulo)
            
        # Sincronización rítmica del sustrato (n!)
        if (t * (delta_phi * C_UNIVERSAL)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ DE IDENTIDAD NATURAL ---
st.title("🛡️ Motor v55: Reconstrucción de Identidad")
st.markdown("### El caos es solo un orden no trayectado.")

# Puerto de Entrada Único: Capacidad de lectura de ADN pura
input_adn = st.text_area(
    "Inyectar ADN (Secuencia Mn):", 
    placeholder="Pega aquí las frecuencias (Ej: 783.99, 0, 932.33...)",
    help="El sistema es una Tabula Rasa. No hay biblioteca. Solo existe lo que tú inyectas."
)

if input_adn:
    try:
        # Transformación del ADN en Momentum Mn
        adn_lista = [float(x.strip()) for x in input_adn.split(",")]
        
        # Cálculo del Diferencial de Fase (ΔΦ) con resolución infinitesimal
        d_phi = extraer_delta_phi(adn_lista)
        
        st.info(f"**Identidad Trayectorial (ΔΦ):** `{d_phi:.15f}`")
        
        if st.button("🔥 MANIFESTAR M0
