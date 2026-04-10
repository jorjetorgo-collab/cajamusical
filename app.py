import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA DE TORRES ---
def ejecutar_igualacion_final(audio_data, delta_phi):
    """
    Implementación del Trayector: Reordena el sustrato n! 
    basado en la definición de fase infinitesimal.
    """
    # Forzamos 64 bits para mantener la precisión de 15 decimales
    n_samples = len(audio_data)
    t = np.linspace(0, 1, n_samples, dtype=np.float64)
    
    # El Trayector: Definimos la nueva posición de cada muestra
    # La desentropía mapea el caos hacia la nueva trayectoria
    nueva_trayectoria = (t * delta_phi) % 1.0
    
    # Mapeo de índices determinista
    indices = (nueva_trayectoria * (n_samples - 1)).astype(np.int64)
    
    return audio_data[indices]

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Trayector Torres", page_icon="🛡️")

st.title("🛡️ Sistema de Desentropía: Identidad Invariante")
st.markdown("### Transmutación de Fase Sonora (Teorema de Torres)")

# Configuración en barra lateral
st.sidebar.header("Parámetros")
delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=1.618033988749895, 
    step=1e-15
)

# Carga de archivo
archivo = st.file_uploader("Subir Canción Base (.wav)", type=["wav"])

if archivo is not None:
    # Leer el wav sin librerías externas pesadas
    rate, data = wavfile.read(archivo)
    
    # Asegurar que sea mono para no corromper la fase
    if len(data.shape) > 1:
        data = data[:, 0]
    
    st.info(f"Sustrato cargado: {len(data)} muestras. Precisión: 15 decimales.")
    
    if st.button("Ejecutar Igualación Final"):
        with st.spinner("Procesando trayectoria..."):
            # Aplicar el modelo
            resultado = ejecutar_igualacion_final(data, delta_phi)
            
            # Crear buffer de salida
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado.astype(np.int16))
            
            st.success("Transmutación completada.")
            st.audio(buffer, format='audio/wav')
            st.download_button(
                label="Descargar M_n",
                data=buffer,
                file_name="salida_torres.wav",
                mime="audio/wav"
            )

st.divider()
st.caption("Determinismo de Fase: La incertidumbre es una deficiencia del observador.")
