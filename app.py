import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE TRAYECTORIA DINÁMICA v21 ---
def motor_torres_dinamico(biblioteca_wav, delta_phi, rate):
    # 1. Preparación del sustrato M0 (Nokia 3310)
    # Normalizamos para que el Demonio de Laplace no tenga picos de saturación
    sustrato = biblioteca_wav.astype(np.float64) / (np.max(np.abs(biblioteca_wav)) + 1e-9)
    n_samples_lib = len(sustrato)
    
    # Identificamos zonas de energía (filtramos los silencios entre teclas)
    umbral = 0.05
    indices_activos = np.where(np.abs(sustrato) > umbral)[0]
    
    if len(indices_activos) == 0:
        # Si no hay sonido, devolvemos silencio absoluto de 8-bit
        return (np.zeros(rate * 5) + 128).astype(np.uint8)

    # 2. Mn: El momentum observado (Establecemos 12 segundos de manifestación)
    duracion_out = 12
    n_samples_out = rate * duracion_out
    resultado_mn = np.zeros(n_samples_out)
    
    # 3. EL TRAYECTOR (N): Escala de búsqueda con "Paso de Humano"
    t = np.arange(n_samples_out) / rate
    
    # Explicación del ajuste: 
    # np.floor crea "peldaños". El trayector pisa una nota, la sostiene y luego salta.
    # El delta_phi controla la velocidad de esa caminata por la biblioteca de Nokia.
    ritmo_escaneo = 8.0 # Ajuste de cadencia para que no suene a "alien" acelerado
    indices_mapeados = (np.floor(t * delta_phi * ritmo_escaneo) * (rate / 4)) % len(indices_activos)
    
    for i in range(n_samples_out):
        # Seleccionamos el átomo de identidad basado en el mapa de energía
        idx_fase = int(indices_mapeados[i])
        resultado_mn[i] = sustrato[indices_activos[idx_fase]]
        
    # 4. AUDITORÍA DEL HORIZONTE (Salida 8-bit Estable)
    # Añadimos un pequeño suavizado para eliminar el "clic" entre saltos de bits
    suavizado = int(rate * 0.002) # 2ms de transición
    if suavizado > 0:
        ventana = np.ones(suavizado) / suavizado
        resultado_mn = np.convolve(resultado_mn, ventana, mode='same')

    mn_max = np.max(np.abs(resultado_mn)) if np.max(np.abs(resultado_mn)) > 0 else 1
    # Conversión final a uint8 (0-255) para soberanía 8-bit
    return (127 * (resultado_mn / mn_max) + 128).astype(np.uint8)

# --- INTERFAZ DEL OBSERVADOR ---
st.set_page_config(page_title="🛡️ Torres v21 - Nokia Scanner", page_icon="📶")
st.title("🛡️ Trayector v21: Scanner de Identidad")
st.markdown("""
### Auditoría de Identidad sobre Sustrato 3310
Este motor busca la resonancia de **Para Elisa** (o cualquier Mn) dentro de los átomos de sonido de un Nokia.
""")

# El valor maestro de 15 decimales que sintoniza la realidad
delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

st.sidebar.info("El ΔΦ actúa como el sintonizador de radio para encontrar la melodía en el caos.")

archivo = st.file_uploader("Subir Tonos Nokia 3310 (M0)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    # Forzar a mono si es necesario
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Manifestar Identidad"):
        with st.spinner("Sincronizando fases alienígenas..."):
            resultado = motor_torres_dinamico(data, delta_phi, rate)
            
            # Generación del buffer de audio
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            
            st.success("Igualación final: Mn manifestada.")
            st.audio(buffer, format='audio/wav
