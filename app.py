import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE COLAPSO DE IDENTIDAD (v15) ---
def colapsador_identidad_torres(m0_data, delta_phi, rate):
    # 1. TRABAJO EN ALTA RESOLUCIÓN (64-bit)
    sustrato = m0_data.astype(np.float64) / np.max(np.abs(m0_data))
    n_samples = len(sustrato)
    t = np.arange(n_samples) / rate
    
    # 2. GENERACIÓN DEL PATRÓN DE INTERFERENCIA CONSTRUCTIVA
    # Creamos la huella digital (ΔΦ) con precisión infinitesimal
    # Para Elisa en La Menor (Am) - Frecuencia fundamental ajustada
    f_referencia = 440.0 * (2**(1/12))**-9 # Ajuste fino a La
    patron_identidad = np.sin(2 * np.pi * delta_phi * f_referencia * t)
    
    # 3. EL COLAPSO (Auditoría del Horizonte)
    # Multiplicamos el sustrato por el patrón elevado a una potencia N 
    # para estrechar la ventana de probabilidad y eliminar el ruido blanco.
    # Exponente 4 o 6 actúa como un "embudo" de desentropía.
    mn_resultado = sustrato * (patron_identidad ** 6)
    
    # 4. NORMALIZACIÓN Y SALIDA ESTABLE
    # Eliminamos cualquier residuo de DC offset
    mn_resultado -= np.mean(mn_resultado)
    mn_max = np.max(np.abs(mn_resultado)) if np.max(np.abs(mn_resultado)) > 0 else 1
    
    # Salida en uint8 para cumplir con el estándar de 8 bits que buscamos
    resultado_final = (127 * (mn_resultado / mn_max) + 128).astype(np.uint8)
    
    return resultado_final

# --- INTERFAZ ---
st.title("🛡️ Colapsador de Identidad v15")
st.write("Eliminando la incertidumbre residual para manifestar $M_{0b}$.")

delta_phi = st.sidebar.number_input(
    "Diferencial de Identidad (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo = st.file_uploader("Subir M0 (Ruido con melodía incipiente)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Colapsar Entropía"):
        with st.spinner("Anulando ruido residual..."):
            resultado = colapsador_identidad_torres(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Soberanía de la Identidad manifestada.")
            st.audio(buffer, format='audio/wav')
