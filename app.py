import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE TRANSMUTACIÓN DE TORRES ---
def generar_m0b(audio_data, delta_phi, rate):
    n_samples = len(audio_data)
    # Tamaño del grano de identidad
    grain_size = int(rate * 0.04) 
    num_grains = n_samples // grain_size
    
    # Creamos el nuevo sustrato vacío
    output = np.zeros(n_samples)
    
    # Generamos una trayectoria no lineal basada en el ΔΦ
    # Esto asegura que no lea a Bach en orden, sino que salte
    # buscando la nueva estructura de Para Elisa.
    t_grain = np.arange(num_grains, dtype=np.float64)
    
    # Esta es la "Llave de Reordenamiento"
    # El ΔΦ altera la posición original de cada grano
    mapeo_caotico = (np.sin(t_grain * delta_phi) * 0.5 + 0.5) * (num_grains - 1)
    indices_reordenados = mapeo_caotico.astype(np.int64)

    for i, idx_bach in enumerate(indices_reordenados):
        # Punto de origen en Bach (M0)
        start_bach = idx_bach * grain_size
        # Punto de destino en el nuevo M0b (Para Elisa)
        start_out = i * grain_size
        
        if start_out + grain_size < n_samples and start_bach + grain_size < n_samples:
            grano = audio_data[start_bach : start_bach + grain_size]
            ventana = np.hanning(grain_size)
            output[start_out : start_out + grain_size] += grano * ventana
            
    return output

# --- INTERFAZ ---
st.set_page_config(page_title="Trayector Torres v4", page_icon="🛡️")
st.title("🛡️ Generador de Sustrato $M_{0b}$")
st.markdown("### Transmutación: Bach $\\rightarrow$ Para Elisa")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=1.618033988749895, # Prueba con Phi o con tus 15 decimales
    step=1e-15
)

archivo = st.file_uploader("Subir Bach 1 (.wav)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Generar Nueva Identidad"):
        with st.spinner("Remapeando muestras..."):
            # Generamos el nuevo sustrato
            resultado = generar_m0b(data, delta_phi, rate)
            
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado.astype(np.int16))
            
            st.success("Sustrato $M_{0b}$ generado con éxito.")
            st.audio(buffer, format='audio/wav')
            st.download_button("Descargar Para Elisa (M0b)", buffer, "m0b_elisa.wav")
