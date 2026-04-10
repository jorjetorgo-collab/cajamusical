import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE FRECUENCIAS DISCRETAS v37 ---
def motor_nokia_torres(delta_phi, rate):
    duracion = 10
    n_samples = int(rate * duracion)
    
    # El Sustrato (M0): Las frecuencias de la escala temperada (Nokia)
    # Definimos las notas de Para Elisa (Mi5, Re#5, Si4, Re5, Do5, La4)
    notas_elisa = [659.25, 622.25, 659.25, 622.25, 659.25, 493.88, 587.33, 523.25, 440.00]
    
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    for i in range(n_samples):
        t = i / rate
        
        # EL TRAYECTOR Ñ (Escalonado):
        # El tempo de Nokia era rígido. Vamos a usar un pulso de 0.125s (corchea)
        # El delta_phi aquí actúa como el "estiramiento" de la partitura
        indice_nota = int(np.floor(t * 6 * delta_phi)) % len(notas_elisa)
        
        # Ñ selecciona la frecuencia del sustrato
        frecuencia = notas_elisa[indice_nota]
        
        # Generación de Onda Cuadrada (El cristal de Nokia)
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        # La esencia del 3310: ON u OFF (1 o -1)
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        
        # El "silencio" entre notas (el corte de energía)
        # Esto es lo que le da el ritmo de "puntos y rayas"
        if (t * 6 * delta_phi) % 1.0 > 0.9: 
            muestra = 0
            
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Trayector v37: Emulación Nokia 3310")
st.write("Cambiando la Ñ continua por una Ñ de estados discretos.")

delta_phi = st.number_input("ΔΦ (Velocidad de Partitura)", value=1.0, format="%.4f")

if st.button("Ejecutar Tono Nokia"):
    rate = 22050
    audio_data = motor_nokia_torres(delta_phi, rate)
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, audio_data)
    st.success("Tono monofónico generado.")
    st.audio(buffer, format='audio/wav')
