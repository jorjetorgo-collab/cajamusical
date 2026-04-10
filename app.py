import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA GRANULAR ---
def motor_granular_torres(audio_data, delta_phi, rate):
    n_samples = len(audio_data)
    # Tamaño del grano: 50ms para que el oído reconozca la nota
    grain_size = int(rate * 0.05) 
    output = np.zeros(n_samples)
    
    # El ΔΦ ahora controla el "salto" entre granos de Bach
    # 15 decimales de precisión en el paso del puntero
    puntero = 0.0
    
    for i in range(0, n_samples - grain_size, grain_size):
        # Calculamos la posición del siguiente grano usando tu diferencial
        posicion = int(puntero % (n_samples - grain_size))
        
        # Extraemos el grano de identidad de Bach
        grano = audio_data[posicion : posicion + grain_size]
        
        # Aplicamos una ventana para evitar el sonido de "clics" o "hule"
        ventana = np.hanning(grain_size)
        output[i : i + grain_size] += grano * ventana
        
        # El puntero avanza según tu diferencial de fase crítico
        puntero += delta_phi * grain_size
        
    return output

# --- INTERFAZ ---
st.set_page_config(page_title="Trayector Torres v3", page_icon="🛡️")
st.title("🛡️ Trayector v3: Reordenamiento Granular")
st.write("Objetivo: Transmutar Bach en Para Elisa mediante granos de identidad.")

# Parámetros
delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=1.059463094359295, # Relación de semitono
    step=1e-15
)

archivo = st.file_uploader("Subir Bach (.wav)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Ejecutar Transmutación"):
        with st.spinner("Reconstruyendo trayectoria armónica..."):
            resultado = motor_granular_torres(data, delta_phi, rate)
            
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado.astype(np.int16))
            
            st.success("Igualación Final completada.")
            st.audio(buffer, format='audio/wav')
            st.download_button("Descargar M_n", buffer, "elisa_torres.wav")
