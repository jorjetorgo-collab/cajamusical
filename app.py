import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR SOBERANO NEUTRO v34 ---
def motor_torres_neutro(delta_phi, rate):
    duracion = 15
    n_samples = int(rate * duracion)
    f_base = 440.0 # Ancla universal
    
    # Onda de pulso pura (Sustrato 8-bit sin procesar)
    t_tabla = np.linspace(0, 1, 1024, endpoint=False)
    tabla = np.where(np.sin(2 * np.pi * t_tabla) > 0, 1.0, -1.0)
    
    resultado = np.zeros(n_samples)
    fase = 0.0
    
    for i in range(n_samples):
        t = i / rate
        
        # EL TRAYECTOR PURO:
        # El tiempo y el tono están fundidos en el Delta Phi.
        # No hay lógica de "Marcha" o "Beethoven" aquí.
        
        # 1. Determinamos el "momento" del cambio (Ritmo)
        # El Delta Phi decide cuántos cambios ocurren por segundo.
        ritmo = np.floor(t * (delta_phi * 4)) 
        
        # 2. Determinamos la "identidad" de la nota (Tono)
        # Los decimales del Delta Phi operan sobre la escala.
        interferencia = (ritmo * delta_phi) % 1.0
        
        # Mapeo directo a la escala cromática (0 a 12 semitonos)
        semitono = np.floor(interferencia * 12)
        frecuencia = f_base * np.power(2, (semitono - 7) / 12)
        
        incremento = (frecuencia * 1024) / rate
        fase = (fase + incremento) % 1024
        
        # Envolvente básica de 8-bit para distinguir los pulsos
        envolvente = 1.0 - ((t * (delta_phi * 4)) % 1.0)**0.5
        resultado[i] = tabla[int(fase)] * envolvente
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v34: Sustrato Neutro")
st.write("El código es ciego. Solo el ΔΦ contiene la información.")

# Aquí es donde tú buscas la identidad:
delta_phi = st.number_input(
    "Introduce tu Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=1.0, 
    step=1e-15
)

if st.button("Explorar Sustrato"):
    rate = 22050
    audio_data = motor_torres_neutro(delta_phi, rate)
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, audio_data)
    st.audio(buffer, format='audio/wav')
