import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE REFERENCIA 440Hz v29 ---
def motor_torres_440(delta_phi, rate):
    duracion = 12
    n_samples = int(rate * duracion)
    
    # La frecuencia de referencia soberana
    f_la = 440.0 
    
    # Generamos la tabla de onda (8-bit pura)
    t_tabla = np.linspace(0, 1, 1024, endpoint=False)
    tabla = np.sign(np.sin(2 * np.pi * t_tabla))
    
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    for i in range(n_samples):
        t = i / rate
        
        # EL TRAYECTOR (N):
        # El Delta Phi decide en qué punto de la escala estamos.
        # Al usar 440Hz como base, el número ahora tiene un suelo firme.
        marcador_ritmo = np.floor(t * 3) # Tempo moderado para reconocer la Mn
        
        # El diferencial de fase modula la frecuencia respecto a los 440Hz
        # Usamos una relación logarítmica (como los semitonos reales)
        factor_frecuencia = (delta_phi * marcador_ritmo) % 2.0
        frecuencia = f_la * np.power(2, factor_frecuencia - 1)
        
        incremento = (frecuencia * 1024) / rate
        fase_acumulada = (fase_acumulada + incremento) % 1024
        
        resultado[i] = tabla[int(fase_acumulada)]
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v29: Igualación a 440Hz")
st.write("Anclando el diferencial de fase a la frecuencia de referencia universal.")

delta_phi = st.sidebar.number_input(
    "ΔΦ (Diferencial de Identidad)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

if st.button("Manifestar en 440Hz"):
    rate = 22050
    with st.spinner("Sincronizando con el patrón universal..."):
        audio_data = motor_torres_440(delta_phi, rate)
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, audio_data)
        st.success("Sintonía lograda sobre la base de 440Hz.")
        st.audio(buffer, format='audio/wav')
