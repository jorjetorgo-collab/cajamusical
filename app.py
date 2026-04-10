import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE IDENTIDAD ÉPICA v47 ---
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 0.0
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    # La firma de Williams: mucha variación en los saltos
    return np.mean(cambios) * np.std(cambios)

def motor_manifestador(delta_phi, partitura, rate):
    duracion = 8
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # Calibración para Marchas: Tempo estable pero con fuerza
    C = 55.0 
    
    for i in range(n_samples):
        t = i / rate
        # Ñ recorre el genoma de la Fuerza
        ñ = int(np.floor(t * (delta_phi * C))) % len(partitura)
        
        frecuencia = partitura[ñ]
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        # Onda cuadrada Nokia (El cristal piezoeléctrico)
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        
        # Silencio rítmico corto para dar sensación de "Fanfarria"
        if (t * (delta_phi * C)) % 1.0 > 0.85: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v47: El Genoma de la Fuerza")

sw_notas = "392.00, 587.33, 523.25, 493.88, 440.00, 783.99, 587.33"
input_notas = st.text_input("Introduce ADN Musical:", sw_notas)

try:
    notas = [float(x.strip()) for x in input_notas.split(",")]
    d_phi = extraer_delta_phi(notas)
    
    st.write(f"**Identidad Extraída (ΔΦ):** `{d_phi:.15f}`")
    
    if st.button("Manifestar Identidad"):
        audio = motor_manifestador(d_phi, notas, 22050)
        buffer = io.BytesIO()
        wavfile.write(buffer, 22050, audio)
        st.audio(buffer, format='audio/wav')
        
    st.info("Nota como el ΔΦ de Star Wars es 'más ruidoso' que el de Dr. Dre. La complejidad del salto define la identidad.")
except:
    st.error("Error en la cadena de frecuencias.")
