import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE TRAYECTORIA REAL v35 ---
def motor_torres_trayector(delta_phi, rate):
    duracion = 12
    n_samples = int(rate * duracion)
    
    # El sustrato puro (M0): Un ciclo de onda de 8-bits
    t_tabla = np.linspace(0, 1, 1024, endpoint=False)
    tabla = np.sign(np.sin(2 * np.pi * t_tabla))
    
    resultado = np.zeros(n_samples)
    
    # --- CONSTRUCCIÓN DE Ñ ---
    # Ñ no es un número estático, es un acumulador
    N_tilde = 0.0 
    
    for i in range(n_samples):
        # La presión de Delta Phi sobre el tiempo
        # Ñ crece según la voluntad del diferencial
        paso_ñ = (delta_phi * 440.0) / rate
        N_tilde += paso_ñ
        
        # El trayector Ñ recorre el sustrato circularmente
        indice = int(N_tilde * 1024) % 1024
        
        # Aplicamos una modulación de Ñ para que la identidad no sea plana
        # Ñ decide cuándo la fase colapsa o salta
        modulacion_ñ = np.sin(N_tilde * 0.001 * delta_phi)
        
        resultado[i] = tabla[indice] * (0.5 + 0.5 * modulacion_ñ)
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v35: El Vehículo Ñ")
st.write("Aquí Ñ se construye paso a paso integrando el diferencial ΔΦ.")

delta_phi = st.number_input(
    "ΔΦ (La Presión Informativa)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

if st.button("Manifestar Ñ"):
    rate = 22050
    audio_data = motor_torres_trayector(delta_phi, rate)
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, audio_data)
    st.success("Trayector Ñ generado desde el sustrato neutro.")
    st.audio(buffer, format='audio/wav')
