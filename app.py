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
    n_samples = len(audio_data)
    
    # Generamos el vector de tiempo con precisión de 64 bits (15-17 decimales reales)
    t = np.linspace(0, 1, n_samples, dtype=np.float64)
    
    # El Trayector define la nueva trayectoria de la información
    # Aplicamos el diferencial de fase (ΔΦ)
    nueva_trayectoria = (t * delta_phi) % 1.0
    
    # Mapeo de índices: El caos se vuelve orden trayectado
    indices = (nueva_trayectoria * (n_samples - 1)).astype(np.int64)
    
    return audio_data[indices]

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Trayector Torres", page_icon="🛡️")

st.title("🛡️ Sistema de Desentropía")
st.subheader("Identidad Invariante y Transmutación de Fase")

st.markdown("""
De acuerdo al **Teorema de Torres**, la incertidumbre es una deficiencia del observador. 
Este sistema reordena el sustrato de una onda sonora ($M_0$) mediante un diferencial de fase.
""")

# Barra lateral para parámetros técnicos
st.sidebar.header("Configuración del Trayector")
delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=1.618033988749895, # Valor inicial sugerido (Phi)
    step=1e-15
)

# Carga de archivo de audio
archivo = st.file_uploader("Cargar Sustrato Base (.wav)", type=["wav"])

if archivo is not None:
    # Lectura del archivo usando scipy (estándar y ligero)
    rate, data = wavfile.read(archivo)
    
    # Convertir a Mono si es necesario para mantener la integridad de la fase
    if len(data.shape) > 1:
        data = data[:, 0]
    
    st.info(f"Sustrato cargado: {len(data)} muestras detectadas.")
    
    if st.button("Ejecutar Igualación Final"):
        with st.spinner("Trayectando resolución infinitesimal..."):
            try:
                # Ejecución del modelo matemático
                resultado = ejecutar_igualacion_final(data, delta_phi)
                
                # Crear buffer en memoria para la salida
                buffer = io.BytesIO()
                wavfile.write(buffer, rate, resultado.astype(np.int16))
                
                st.success("Transmutación de Identidad completada.")
                
                # Reproductor y botón de descarga
                st.audio(buffer, format='audio/wav')
                st.download_button(
                    label="Descargar M_n Transmutado",
                    data=buffer,
                    file_name="salida_torres.wav",
                    mime="audio/wav"
                )
            except Exception as e:
                st.error(f"Error en la trayectoria: {e}")

st.divider()
st.caption("“La incertidumbre no existe, solo la deficiencia del observador.” — J. Torres")
