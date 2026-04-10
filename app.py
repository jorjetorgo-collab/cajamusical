import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE RECONSTRUCCIÓN CIEGA v19 ---
def motor_ciego_nokia(biblioteca_wav, delta_phi, rate):
    # 1. Preparación del sustrato (n!)
    # Convertimos a float64 para la precisión infinitesimal de Torres
    sustrato = biblioteca_wav.astype(np.float64) / np.max(np.abs(biblioteca_wav))
    n_samples_lib = len(sustrato)
    
    # Mn: El momentum observado que queremos manifestar (15 segundos)
    segundos_salida = 15
    n_samples_out = rate * segundos_salida
    resultado_mn = np.zeros(n_samples_out, dtype=np.float64)
    
    # 2. PROCESO DE IGUALACIÓN FINAL
    # El trayector no conoce las notas. Solo usa el Delta Phi para 
    # decidir en qué punto de la biblioteca de tonos debe estar el "ojo"
    t_out = np.arange(n_samples_out) / rate
    
    # La trayectoria (N) es una función de la curvatura del diferencial de fase
    # multiplicada por una constante de resonancia (1000hz de barrido)
    trayectoria_n = (t_out * delta_phi * 1000) % n_samples_lib
    
    for i in range(n_samples_out):
        idx = int(trayectoria_n[i])
        # Extraemos el átomo de identidad del Nokia
        resultado_mn[i] = sustrato[idx]
        
    # 3. AUDITORÍA DEL HORIZONTE
    # Limpieza de 8-bit para el sonido característico del 3310
    mn_max = np.max(np.abs(resultado_mn)) if np.max(np.abs(resultado_mn)) > 0 else 1
    # Salida en uint8 (estándar 8-bit)
    resultado_uint8 = (127 * (resultado_mn / mn_max) + 128).astype(np.uint8)
    
    return resultado_uint8

# --- INTERFAZ DEL OBSERVADOR ---
st.title("🛡️ Lector de Identidad Ciego v19")
st.write("Sustrato: Tonos Nokia 3310. El código NO conoce la melodía.")

# El valor que "enfoca" la identidad dentro del ruido de tonos
delta_phi = st.sidebar.number_input(
    "Diferencial de Identidad (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo = st.file_uploader("Subir Audio de Tonos 3310 (M0)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Escanear Trayectoria"):
        with st.spinner("Buscando a Beethoven en los átomos del Nokia..."):
            resultado = motor_ciego_nokia(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Igualación final completada.")
            st.audio(buffer, format='audio/wav')
