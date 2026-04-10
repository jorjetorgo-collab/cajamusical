import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA DE TORRES ---
def ejecutar_igualacion_final(audio_data, delta_phi, rate):
    """
    Implementación del Trayector: Reordena el sustrato n! 
    basado en la definición de fase infinitesimal.
    """
    # Aseguramos precisión de 64 bits para los 15 decimales
    n_samples = len(audio_data)
    t = np.linspace(0, 1, n_samples, dtype=np.float64)
    
    # El Trayector: Definimos la nueva posición de cada muestra (M_n)
    # Aplicando el diferencial de fase (ΔΦ) sobre el tiempo lineal
    # Esta es la traducción algorítmica de la sumatoria de tus variables
    nueva_trayectoria = (t * delta_phi) % 1.0
    
    # Mapeo de índices: El caos se vuelve orden trayectado
    indices = (nueva_trayectoria * (n_samples - 1)).astype(np.int64)
    
    return audio_data[indices]

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Trayector Torres", page_icon="🛡️")

st.title("🛡️ Sistema de Desentropía: Identidad Invariante")
st.markdown("""
Este sistema aplica el **Teorema de Torres** para transmutar la trayectoria de una onda sonora 
conservando su identidad inicial ($M_0$). 
""")

# Configuración de variables
st.sidebar.header("Parámetros del Trayector")
delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=1.618033988749895, # Valor por defecto (Phi)
    step=1e-15
)

# Carga de archivo
archivo = st.file_uploader("Subir Canción Base (Sustrato .wav)", type=["wav"])

if archivo is not None:
    # Leer el wav
    rate, data = wavfile.read(archivo)
    
    # Normalizar a mono si es necesario para no romper la fase
    if len(data.shape) > 1:
        data = data[:, 0]
    
    st.info(f"Sustrato cargado con {len(data)} muestras. Resolución: 15 decimales.")
    
    if st.button("Ejecutar Transmutación"):
        with st.spinner("Calculando Identidad Invariante..."):
            # Aplicar el modelo
            audio_transmutado = ejecutar_igualacion_final(data, delta_phi, rate)
            
            # Crear buffer para descarga
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, audio_transmutado.astype(np.int16))
            
            st.success("Igualación Final completada.")
            
            # Reproductor y Descarga
            st.audio(buffer, format='audio/wav')
            st.download_button(
                label="Descargar M_n Transmutado",
                data=buffer,
                file_name="transmutacion_torres.wav",
                mime="audio/wav"
            )

st.divider()
st.caption("La incertidumbre no existe, solo la deficiencia del observador. — Teorema de Torres")
