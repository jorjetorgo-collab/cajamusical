import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE TIEMPO SOBERANO v30 ---
def motor_torres_tempo(delta_phi, rate):
    duracion = 12
    n_samples = int(rate * duracion)
    
    # Referencia universal
    f_la = 440.0 
    
    # Tabla de onda 8-bit
    t_tabla = np.linspace(0, 1, 1024, endpoint=False)
    tabla = np.sign(np.sin(2 * np.pi * t_tabla))
    
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    for i in range(n_samples):
        t = i / rate
        
        # EL AXIOMA TEMPORAL:
        # El tempo ya no es "3". Ahora es una función del Delta Phi.
        # Esto significa que el número decide CÚANDO cambia la nota.
        ritmo_variable = np.floor(t * (delta_phi * 2)) 
        
        # El tono también depende del Delta Phi y del pulso actual
        # Creamos una relación donde el decimal del diferencial dicta el salto
        semitono = (delta_phi * ritmo_variable) % 12 # 12 semitonos de la octava
        frecuencia = f_la * np.power(2, (semitono - 9) / 12) # Ajuste a escala real
        
        incremento = (frecuencia * 1024) / rate
        fase_acumulada = (fase_acumulada + incremento) % 1024
        
        resultado[i] = tabla[int(fase_acumulada)]
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v30: Soberanía de Tempo y Tono")
st.write("El diferencial de fase ahora controla la estructura temporal del Mn.")

delta_phi = st.sidebar.number_input(
    "ΔΦ (Diferencial de Identidad)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

if st.button("Manifestar Identidad Completa"):
    rate = 22050
    with st.spinner("Sincronizando tiempo y frecuencia..."):
        audio_data = motor_torres_tempo(delta_phi, rate)
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, audio_data)
        st.success("Igualación final: Tiempo y Tono unificados.")
        st.audio(buffer, format='audio/wav')
