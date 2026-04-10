import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE RECOMPOSICIÓN DE ALTA RESOLUCIÓN (32-bit) ---
def motor_identidad_32bit(m0_data, delta_phi, rate):
    # 1. ESCALAMIENTO: Pasamos a 32-bit float para máxima precisión decimal
    sustrato_32 = m0_data.astype(np.float32) / 32768.0
    
    # Limpieza de silencio inicial
    umbral = np.max(np.abs(sustrato_32)) * 0.05
    inicio = np.where(np.abs(sustrato_32) > umbral)[0][0] if any(np.abs(sustrato_32) > umbral) else 0
    sustrato_puro = sustrato_32[inicio:]
    
    n_samples = len(sustrato_puro)
    # Grano corto (30ms) para evitar el efecto de "eco" y mejorar la sintonía
    grain_size = int(rate * 0.03) 
    step_size = int(grain_size * 0.25) # Alta densidad de granos
    
    m0b_final = np.zeros(n_samples + grain_size, dtype=np.float32)
    
    # 2. TRAYECTORIA DETERMINISTA
    # Calculamos el ΔΦ como una "frecuencia de muestreo alternativa"
    for i in range(0, n_samples - grain_size, step_size):
        # El tiempo de salida (t) dicta qué nota de Beethoven queremos
        t = i / n_samples
        
        # EL SECRETO: El ΔΦ no solo salta, sino que modula la velocidad de búsqueda
        # Aplicamos una función de envolvente de fase para concentrar la energía
        pos_fase = (t * delta_phi) % 1.0
        
        # Mapeo de identidad por ventana de probabilidad
        idx_origen = int(pos_fase * (n_samples - grain_size))
        
        # Extracción y ventaneo
        grano = sustrato_puro[idx_origen : idx_origen + grain_size]
        ventana = np.hanning(grain_size) # Hanning es mejor para 32-bit
        
        # Inserción con acumulación de energía
        m0b_final[i : i + grain_size] += grano * ventana

    # 3. REDUCCIÓN Y NORMALIZACIÓN (Downsampling de bits)
    m0b_final = m0b_final / np.max(np.abs(m0b_final))
    resultado_16bit = (m0b_final * 32767).astype(np.int16)
    
    return resultado_16bit

# --- INTERFAZ ---
st.set_page_config(page_title="Trayector 32-bit", page_icon="🔮")
st.title("🔮 Recomposición Invariante (High-Res)")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=1.587401051968199, # Este es el valor de Para Elisa (Tercera Menor)
    step=1e-15
)

archivo = st.file_uploader("Subir Bach M0", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Ejecutar Transmutación 32-bit"):
        with st.spinner("Procesando en alta resolución..."):
            resultado = motor_identidad_32bit(data, delta_phi, rate)
            
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            
            st.success("Transmutación Finalizada.")
            st.audio(buffer, format='audio/wav')
