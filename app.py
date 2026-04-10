import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE RESONANCIA DE TORRES v20 ---
def motor_resonante_ciego(biblioteca_wav, delta_phi, rate):
    # 1. Preparación del sustrato (n!)
    sustrato = biblioteca_wav.astype(np.float64) / np.max(np.abs(biblioteca_wav))
    n_samples_lib = len(sustrato)
    
    # 2. Identificación de "Átomos con Energía"
    # Buscamos solo las partes del audio del Nokia donde NO hay silencio
    umbral = 0.1
    indices_activos = np.where(np.abs(sustrato) > umbral)[0]
    
    if len(indices_activos) == 0:
        return (np.zeros(rate * 5) + 128).astype(np.uint8)

    # 3. Construcción del Momentum Mn
    duracion_out = 10
    n_samples_out = rate * duracion_out
    resultado_mn = np.zeros(n_samples_out)
    
    # El trayector recorre el tiempo
    for i in range(n_samples_out):
        t = i / rate
        
        # EL AXIOMA: El Delta Phi decide cuál de los "átomos activos" 
        # del Nokia se manifiesta en este microsegundo.
        # Esta es la sumatoria integral de la fase.
        idx_lookup = int((t * delta_phi * 500) % len(indices_activos))
        
        # Extraemos la identidad del sustrato activo
        resultado_mn[i] = sustrato[indices_activos[idx_lookup]]
        
    # 4. Auditoría del Horizonte (8-bit)
    mn_max = np.max(np.abs(resultado_mn)) if np.max(np.abs(resultado_mn)) > 0 else 1
    return (127 * (resultado_mn / mn_max) + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v20: Resonancia de Átomos")
st.write("Eliminando el silencio del sustrato para revelar el Momentum $M_n$.")

delta_phi = st.sidebar.number_input(
    "ΔΦ (Frecuencia de Identidad)", 
    format="%.15f", 
    value=1.618033988749895, # Probemos con Phi para buscar armonía natural
    step=1e-15
)

archivo = st.file_uploader("Subir Tonos 3310", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Sintonizar Identidad"):
        with st.spinner("Filtrando entropía del sustrato..."):
            resultado = motor_resonante_ciego(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Igualación final manifestada.")
            st.audio(buffer, format='audio/wav')
