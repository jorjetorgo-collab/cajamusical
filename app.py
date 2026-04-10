import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE IDENTIDAD INVARIANTE v26 ---
def motor_torres_wavetable(delta_phi, rate):
    duracion = 10
    n_samples = int(rate * duracion)
    
    # 1. Creamos un ciclo de onda pura (El Átomo)
    # Una simple onda cuadrada de 256 muestras
    tamaño_tabla = 256
    tabla = np.sign(np.sin(2 * np.pi * np.linspace(0, 1, tamaño_tabla, endpoint=False)))
    
    resultado = np.zeros(n_samples)
    posicion = 0.0
    
    # 2. EL TRAYECTOR (N):
    # La velocidad de lectura de la tabla depende de Delta Phi.
    # Sintonizamos para que el rango de frecuencias sea captable (200Hz - 2000Hz)
    frecuencia_maestra = (delta_phi * 100) % 1000 + 200
    
    for i in range(n_samples):
        # El incremento de fase dictado por la ley de Torres
        incremento = (frecuencia_maestra * tamaño_tabla) / rate
        posicion = (posicion + incremento) % tamaño_tabla
        
        # Aplicamos una modulación rítmica basada en los decimales de delta_phi
        # Esto creará los "saltos" de la melodía
        modulador_ritmo = np.floor(i / (rate * 0.2)) # Cambia cada 0.2 segundos
        if (int(modulador_ritmo * delta_phi) % 2) == 0:
            resultado[i] = tabla[int(posicion)]
        else:
            # Salto armónico (Identidad Mn)
            posicion_armonica = (posicion * 1.5) % tamaño_tabla
            resultado[i] = tabla[int(posicion_armonica)]
            
    # 3. Auditoría del Horizonte (8-bit)
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.set_page_config(page_title="🛡️ Torres v26 - Wavetable", page_icon="📡")
st.title("🛡️ Trayector v26: Motor de Identidad Invariante")
st.write("Generación mediante Tabla de Ondas. La melodía emerge del diferencial de fase.")

delta_phi = st.sidebar.number_input(
    "Diferencial de Identidad (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

if st.button("Sintonizar Mn"):
    rate = 22050
    with st.spinner("Estabilizando frecuencia portadora..."):
        audio_data = motor_torres_wavetable(delta_phi, rate)
        
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, audio_data)
        
        st.success("Señal de identidad sintonizada.")
        st.audio(buffer, format='audio/wav')
