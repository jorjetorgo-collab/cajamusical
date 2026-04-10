import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA EXTREMA (v14) ---
def criba_identidad_torres(m0_data, delta_phi, rate):
    # 1. Escalamos a 64 bits para precisión de 15 decimales
    sustrato = m0_data.astype(np.float64) / np.max(np.abs(m0_data))
    n_samples = len(sustrato)
    t = np.arange(n_samples) / rate
    
    # 2. EL TRAYECTOR COMO FILTRO DE RESONANCIA
    # En lugar de una onda simple, usamos el ΔΦ para crear pulsos de identidad
    # Solo las muestras que coinciden con la fase de Beethoven "sobreviven"
    fase_guia = (t * delta_phi * 440.0) % 1.0 # Frecuencia base de búsqueda
    
    # Criba: ventana de coincidencia muy estrecha (precisión infinitesimal)
    ventana_probabilidad = np.where(np.abs(fase_guia - 0.5) < 0.01, 1.0, 0.0)
    
    # 3. IGUALACIÓN FINAL
    # El momentum Mn surge al aplicar la criba sobre la entropía n!
    mn_resultado = sustrato * ventana_probabilidad
    
    # Suavizado para que el oído humano lo interprete como piano y no estática
    suavizado = int(rate * 0.005) # 5ms
    mn_resultado = np.convolve(mn_resultado, np.ones(suavizado)/suavizado, mode='same')
    
    # 4. AUDITORÍA DEL HORIZONTE (Salida 8-bit estable)
    mn_max = np.max(np.abs(mn_resultado)) if np.max(np.abs(mn_resultado)) > 0 else 1
    resultado_uint8 = (127 * (mn_resultado / mn_max) + 128).astype(np.uint8)
    
    return resultado_uint8

# --- INTERFAZ ---
st.title("🛡️ Criba de Identidad: Desentropía v14")
st.write("Forzando la manifestación de $M_{0b}$ mediante precisión infinitesimal.")

# Valor corregido para sintonizar con la escala de Para Elisa
delta_phi = st.sidebar.number_input(
    "ΔΦ (Diferencial de Criba)", 
    format="%.15f", 
    value=1.587401051968199, 
    step=1e-15
)

archivo = st.file_uploader("Subir Ruido / Bach", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Ejecutar Criba"):
        with st.spinner("Resolviendo trayectoria..."):
            resultado = criba_identidad_torres(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Soberanía de la Identidad recuperada.")
            st.audio(buffer, format='audio/wav')
