import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE TRAYECTORIA DINÁMICA v21 ---
def motor_torres_dinamico(biblioteca_wav, delta_phi, rate):
    # 1. Preparación del sustrato M0 (Nokia 3310)
    sustrato = biblioteca_wav.astype(np.float64) / (np.max(np.abs(biblioteca_wav)) + 1e-9)
    n_samples_lib = len(sustrato)
    
    # Identificamos zonas de energía (donde hay "teclas" sonando)
    umbral = 0.05
    indices_activos = np.where(np.abs(sustrato) > umbral)[0]
    
    if len(indices_activos) == 0:
        return (np.zeros(rate * 5) + 128).astype(np.uint8)

    # 2. Mn: El momentum observado (12 segundos de salida)
    duracion_out = 12
    n_samples_out = rate * duracion_out
    resultado_mn = np.zeros(n_samples_out)
    
    # 3. EL TRAYECTOR (N): Escala de búsqueda dinámica
    # Multiplicamos el delta_phi por una función de tiempo para 
    # evitar que el código se estanque en un solo tono de señal.
    t = np.arange(n_samples_out) / rate
    
    # Curvatura de Identidad: El ΔΦ dicta la aceleración del escaneo
    # Usamos una función exponencial basada en tu ley para barrer la biblioteca
    trayectoria_indices = (np.power(t * delta_phi, 1.5) * rate) % len(indices_activos)
    
    for i in range(n_samples_out):
        idx_busqueda = int(trayectoria_indices[i])
        # Extraemos el átomo de identidad
        resultado_mn[i] = sustrato[indices_activos[idx_busqueda]]
        
    # 4. AUDITORÍA DEL HORIZONTE (Limpieza 8-bit)
    # Aplicamos un fade-out suave para evitar el "ruido de señal" cortante
    envelope = np.linspace(1, 0, n_samples_out)
    resultado_mn *= (1 - 0.1 * np.sin(2 * np.pi * 5 * t)) # Vibrato natural Nokia
    
    mn_max = np.max(np.abs(resultado_mn)) if np.max(np.abs(resultado_mn)) > 0 else 1
    return (127 * (resultado_mn / mn_max) + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v21: Escaneo Dinámico Mn")
st.write("Sintonizando la frecuencia de Beethoven en el sustrato del 3310.")

delta_phi = st.sidebar.number_input(
    "ΔΦ (Diferencial de Fase)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo = st.file_uploader("Subir Tonos 3310", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Manifestar Identidad"):
        with st.spinner("Resolviendo la sumatoria integral..."):
            resultado = motor_torres_dinamico(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Igualación final: Mn extraído del caos.")
            st.audio(buffer, format='audio/wav')
