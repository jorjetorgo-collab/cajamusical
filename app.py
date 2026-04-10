import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR CIEGO (ΔΦ) ---
# No conoce canciones. Extrae la huella del Momentum Observado (Mn).
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    # Diferencial de fase: relación de cambio pura entre estados.
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    # La firma del trayector que cancela la entropía.
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
        # Localiza el orden escondido mediante la sumatoria integral.
        ñ_idx = int(np.floor(t * (delta_phi * C_UNIVERSAL))) % len(adn_inyectado)
        
        frecuencia = adn_inyectado[ñ_idx]
        
        if frecuencia > 0:
            incremento = (2 * np.pi * frecuencia) / rate
            fase_acumulada += incremento
            # Manifestación física de la identidad conservada (M0).
            muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        else:
            muestra = 0 # Silencio absoluto: ausencia de momentum.
            
        # Sincronización rítmica: la estructura del sustrato (n!).
        if (t * (delta_phi * C_UNIVERSAL)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ DE SOBERANÍA ABSOLUTA ---
st.title("🛡️ Motor v55: Tabula Rasa")
st.markdown("### El caos es solo un orden no trayectado.")

# Puerto de Entrada Único (Sin precargas ni bibliotecas)
input_adn = st.text_area(
    "Inyectar ADN (Secuencia de Frecuencias Mn):", 
    placeholder="Escribe aquí las frecuencias separadas por coma...",
    help="El sistema no tiene memoria. Tú eres el único que posee la Identidad inicial (M0)."
)

if input_adn:
    try:
        # Transformación del ADN en Momentum Mn.
        adn_lista = [float(x.strip()) for x in input_adn.split(",")]
        
        # Cálculo del Diferencial de Fase (ΔΦ).
        d_phi = extraer_delta_phi(adn_lista)
        
        st.info(f"**Identidad Trayectorial (ΔΦ):** `{d_phi:.15f}`")
        
        if st.button("🔥 RECLAMAR IDENTIDAD (M0)"):
            # Proceso de Igualación Final.
            audio_buffer = motor_torres_puro(d_phi, adn_lista)
            
            output = io.BytesIO()
            wavfile.write(output, 22050, audio_buffer)
            st.audio(output, format='audio/wav')
            st.success("Desentropía completada: Identidad Natural manifestada.")

    except Exception as e:
        st.error(f"Error en la resolución del trayector: {e}")
else:
    st.write("Esperando entrada para cancelar la incertidumbre estructural.")
