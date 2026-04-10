import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE IDENTIDAD POR INTERFERENCIA v32 ---
def motor_torres_interferencia(delta_phi, rate):
    duracion = 12
    n_samples = int(rate * duracion)
    f_la = 440.0 
    
    t_tabla = np.linspace(0, 1, 1024, endpoint=False)
    tabla = np.sign(np.sin(2 * np.pi * t_tabla))
    
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    for i in range(n_samples):
        t = i / rate
        
        # EL SALTO DE IDENTIDAD:
        # En lugar de una escala lineal, usamos el Delta Phi para crear 
        # una "huella" de notas. 
        # Si el número es correcto, la interferencia creará el Mi-Re#-Mi
        pulso = np.floor(t * 6) # Un tempo más ágil
        
        # Esta es la "curvatura" del trayector:
        # Usamos el diferencial para decidir qué tan lejos salta la nota
        # respecto a la base de 440Hz.
        decisión_nota = (pulso * delta_phi) % 1.0
        
        # Mapeamos a la escala cromática (12 notas)
        # 7 semitonos = Quinta justa; 1 semitono = Segunda menor
        semitono = np.floor(decisión_nota * 12)
        
        frecuencia = f_la * np.power(2, (semitono - 5) / 12) 
        
        incremento = (frecuencia * 1024) / rate
        fase_acumulada = (fase_acumulada + incremento) % 1024
        
        # Envolvente para separar las notas (Staccato)
        envolvente = 1.0 - ((t * 6) % 1.0)**0.5
        resultado[i] = tabla[int(fase_acumulada)] * envolvente
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v32: De Escala a Identidad")

delta_phi = st.sidebar.number_input(
    "ΔΦ (Diferencial de Identidad)", 
    format="%.15f", 
    value=1.498307076876681, 
    step=1e-15
)

if st.button("Sintonizar Melodía"):
    rate = 22050
    with st.spinner("Saliendo de la escala lineal..."):
        audio_data = motor_torres_interferencia(delta_phi, rate)
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, audio_data)
        st.success("Sustrato sintonizado. Escuchando la Mn.")
        st.audio(buffer, format='audio/wav')
