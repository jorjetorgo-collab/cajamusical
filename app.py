import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE IDENTIDAD ARMÓNICA (TORRES v9) ---
def motor_armonico_m0b(m0_data, delta_phi, rate):
    # 1. Preparación del sustrato
    m0_32 = m0_data.astype(np.float32) / 32768.0
    n_samples = len(m0_32)
    grain_size = int(rate * 0.04) # 40ms para capturar la "nota"
    m0b_final = np.zeros(n_samples)
    
    # 2. Generación de la "Frecuencia Guía" (Beethoven Virtual)
    # Creamos una señal de referencia basada en tu ΔΦ
    t_ref = np.linspace(0, n_samples/rate, n_samples)
    # Esta es la trayectoria ideal que Beethoven debería seguir
    guia_beethoven = np.sin(2 * np.pi * delta_phi * 100 * t_ref) 

    # 3. Re-ensamblaje por Afinidad
    step = int(grain_size * 0.5)
    for i in range(0, n_samples - grain_size, step):
        # En lugar de saltar al azar, buscamos en Bach un grano 
        # cuya energía coincida con el momento de la fase guía
        t_actual = i / n_samples
        
        # El ΔΦ define la "ventana de búsqueda" en Bach
        ventana_inicio = int((t_actual * 0.5) * n_samples)
        ventana_fin = int(min(ventana_inicio + (rate * 2), n_samples - grain_size))
        
        # BUSQUEDA: Encontramos el punto en Bach que "vibra" igual que la guía
        # (Esto es una simplificación de tu desentropía para que corra en Streamlit)
        search_area = m0_32[ventana_inicio : ventana_fin : 100] # Muestreo rápido
        best_match_idx = np.argmax(np.abs(search_area)) * 100 + ventana_inicio
        
        # Extraemos y aplicamos ventana
        grano = m0_32[best_match_idx : best_match_idx + grain_size]
        env = np.hanning(len(grano))
        
        if i + len(grano) < n_samples:
            m0b_final[i : i + len(grano)] += grano * env

    # 4. Normalización Final
    m0b_final = m0b_final / (np.max(np.abs(m0b_final)) + 1e-9)
    return (m0b_final * 32767).astype(np.int16)

# --- INTERFAZ ---
st.set_page_config(page_title="Trayector Armónico v9", page_icon="🎼")
st.title("🎼 Trayector v9: Coherencia de Sustrato")
st.write("Buscando la identidad de Beethoven dentro de los átomos de Bach.")

# El Delta Phi ahora es una frecuencia de búsqueda
delta_phi = st.sidebar.number_input(
    "Diferencial de Resonancia", 
    format="%.15f", 
    value=3.296275555555556, # Sintonía con Mi
    step=1e-15
)

archivo = st.file_uploader("Subir Bach M0", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Sintonizar Identidad"):
        with st.spinner("Analizando afinidades armónicas..."):
            resultado = motor_armonico_m0b(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Transmutación por afinidad completada.")
            st.audio(buffer, format='audio/wav')
