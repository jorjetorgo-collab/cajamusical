import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA PURA (TORRES v7) ---
def reconstruccion_total_m0b(m0_data, delta_phi, rate):
    # 1. LIMPIEZA DE IDENTIDAD: Eliminamos silencios iniciales (títulos del video)
    # Buscamos dónde empieza la energía real del piano
    umbral = np.max(np.abs(m0_data)) * 0.05
    inicio_real = np.where(np.abs(m0_data) > umbral)[0][0] if any(np.abs(m0_data) > umbral) else 0
    sustrato_puro = m0_data[inicio_real:]
    
    n_samples = len(sustrato_puro)
    grain_size = int(rate * 0.05) 
    step_size = int(grain_size * 0.5)
    
    # Creamos un lienzo totalmente vacío (Silencio absoluto)
    m0b_final = np.zeros(n_samples)
    
    # 2. RECOMPOSICIÓN DESDE CERO
    # No usamos el tiempo de Bach. Usamos la trayectoria del Delta Phi
    # para decidir qué "átomo" de Bach va en qué lugar de Beethoven.
    for i in range(0, n_samples - grain_size, step_size):
        # El ΔΦ es el "imán" que extrae la muestra
        # Calculamos una posición no lineal para romper el orden de Bach
        t = i / n_samples
        
        # Mapeo Exponencial de Fase: Ignora el orden original
        # El delta_phi aquí debe ser el diferencial que calculamos para Elisa
        fase_remapeada = (np.abs(np.sin(t * np.pi * delta_phi))) % 1.0
        idx_origen = int(fase_remapeada * (n_samples - grain_size))
        
        # Extraemos solo el "color" del piano (la identidad)
        grano = sustrato_puro[idx_origen : idx_origen + grain_size].astype(np.float32)
        
        # Aplicamos ventana para que no suene a "trastes"
        ventana = np.blackman(grain_size)
        
        # Insertamos en la nueva línea de tiempo
        if i + grain_size < n_samples:
            m0b_final[i : i + grain_size] += grano * ventana

    # Normalización y limpieza de ruido de fondo
    m0b_final = (m0b_final / np.max(np.abs(m0b_final)) * 32767).astype(np.int16)
    return m0b_final

# --- INTERFAZ ---
st.set_page_config(page_title="Trayector Torres v7", page_icon="🛡️")
st.title("🛡️ Recomposición de Identidad Invariante")
st.write("Generando $M_{0b}$ (Para Elisa) desde el sustrato atómico de Bach.")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase Recalculado", 
    format="%.15f", 
    value=2.721055555555556, # El valor que sintoniza con Mi
    step=1e-15
)

archivo = st.file_uploader("Subir Bach M0 (con silencios de video)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Recomponer desde Cero"):
        with st.spinner("Desintegrando M0 y ensamblando M0b..."):
            resultado = reconstruccion_total_m0b(data, delta_phi, rate)
            
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            
            st.success("Identidad $M_{0b}$ reconstruida.")
            st.audio(buffer, format='audio/wav')
            st.download_button("Descargar M0b Puro", buffer, "identidad_recompuesta.wav")
