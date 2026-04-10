import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE TRAYECTORIA DINÁMICA v21.1 ---
def motor_torres_dinamico(biblioteca_wav, delta_phi, rate):
    # 1. Preparación del sustrato M0 (Nokia 3310)
    # Normalización para asegurar la soberanía de la amplitud
    sustrato = biblioteca_wav.astype(np.float64) / (np.max(np.abs(biblioteca_wav)) + 1e-9)
    n_samples_lib = len(sustrato)
    
    # Identificamos zonas de energía (filtramos silencios)
    umbral = 0.05
    indices_activos = np.where(np.abs(sustrato) > umbral)[0]
    
    if len(indices_activos) == 0:
        return (np.zeros(rate * 5) + 128).astype(np.uint8)

    # 2. Mn: El momentum observado (12 segundos)
    duracion_out = 12
    n_samples_out = int(rate * duracion_out)
    resultado_mn = np.zeros(n_samples_out)
    
    # 3. EL TRAYECTOR (N): Escala de búsqueda con "Paso de Humano"
    t = np.arange(n_samples_out) / rate
    
    # Ritmo de escaneo: La velocidad a la que el trayector pisa los átomos
    ritmo_escaneo = 8.0 
    indices_mapeados = (np.floor(t * delta_phi * ritmo_escaneo) * (rate / 4)) % len(indices_activos)
    
    for i in range(n_samples_out):
        idx_fase = int(indices_mapeados[i])
        resultado_mn[i] = sustrato[indices_activos[idx_fase]]
        
    # 4. AUDITORÍA DEL HORIZONTE (Salida 8-bit Estable)
    suavizado = int(rate * 0.002) 
    if suavizado > 1:
        ventana = np.ones(suavizado) / suavizado
        resultado_mn = np.convolve(resultado_mn, ventana, mode='same')

    mn_max = np.max(np.abs(resultado_mn)) if np.max(np.abs(resultado_mn)) > 0 else 1
    return (127 * (resultado_mn / mn_max) + 128).astype(np.uint8)

# --- INTERFAZ DEL OBSERVADOR ---
st.set_page_config(page_title="🛡️ Torres v21.1 - Nokia Scanner", page_icon="📶")
st.title("🛡️ Trayector v21.1: Scanner de Identidad")

# Sintonizador de Fase
delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

st.sidebar.markdown("---")
st.sidebar.write("Ajuste del Observador: 15 decimales de precisión.")

# Carga de archivo
archivo = st.file_uploader("Subir Tonos Nokia 3310 (M0)", type=["wav"])

if archivo is not None:
    # DEFINICIÓN CRÍTICA DE RATE Y DATA
    rate, data = wavfile.read(archivo)
    
    # Aseguramos que data sea mono
    if len(data.shape) > 1:
        data = data[:, 0]
    
    if st.button("Manifestar Identidad"):
        with st.spinner("Sincronizando fases alienígenas..."):
            # Pasamos las variables rate y data directamente
            resultado = motor_torres_dinamico(data, delta_phi, rate)
            
            # Generación del buffer de salida
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            
            st.success("Igualación final: Mn manifestada.")
            st.audio(buffer, format='audio/wav')
            
            st.download_button(
                label="Descargar Sustrato Mn",
                data=buffer.getvalue(),
                file_name="identidad_nokia_8bit.wav",
                mime="audio/wav"
            )
else:
    st.info("Esper
