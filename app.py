import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE RECONSTRUCCIÓN POR BIBLIOTECA (TORRES v17) ---
def motor_nokia_extensivo(sustrato_audio, delta_phi, rate):
    # 1. DICCIONARIO DE FRECUENCIAS (Identidad Mn)
    # Definimos las notas para una trayectoria más larga
    E5, Dsh5, B4, D5, C5, A4 = 659.25, 622.25, 493.88, 587.33, 523.25, 440.0
    C4, E4, A4_low = 261.63, 329.63, 440.0 # Notas de acompañamiento
    
    # Secuencia extendida de Para Elisa
    frase_1 = [(E5, 0.2), (Dsh5, 0.2), (E5, 0.2), (Dsh5, 0.2), (E5, 0.2), (B4, 0.2), (D5, 0.2), (C5, 0.2), (A4, 0.4)]
    frase_2 = [(C4, 0.2), (E4, 0.2), (A4_low, 0.2), (B4, 0.4)]
    melodia_completa = frase_1 + frase_2 + frase_1 + frase_2
    
    resultado_acumulado = []
    
    # 2. PROCESAMIENTO POR TRAYECTORIA
    for i, (frec, dur) in enumerate(melodia_completa):
        t = np.linspace(0, dur, int(rate * dur), endpoint=False)
        
        # Generamos el pulso de 8 bits (Onda Cuadrada Nokia)
        # El delta_phi aquí actúa como el modulador de ancho de pulso (PWM)
        onda = np.sign(np.sin(2 * np.pi * frec * t * (delta_phi / 2.721055555555556)))
        
        # EXTRACCIÓN DEL SUSTRATO (Bach)
        # Usamos el delta_phi para saltar de forma no lineal en el archivo de Bach
        punto_muestreo = int((i * delta_phi * rate * 0.5) % (len(sustrato_audio) - len(t)))
        fragmento_bach = sustrato_audio[punto_muestreo : punto_muestreo + len(t)]
        
        # Si el fragmento es corto, lo rellenamos para no perder la identidad
        if len(fragmento_bach) < len(t):
            fragmento_bach = np.pad(fragmento_bach, (0, len(t) - len(fragmento_bach)))
            
        # IGUALACIÓN: La onda del Nokia se "viste" con los átomos de Bach
        nota_transmutada = onda * (fragmento_bach / np.max(np.abs(fragmento_bach)) if np.max(np.abs(fragmento_bach)) > 0 else 1)
        resultado_acumulado.append(nota_transmutada)
    
    # Concatenamos todos los momentos observados
    mn_final = np.concatenate(resultado_acumulado)
    
    # 3. AUDITORÍA DEL HORIZONTE (8-bit uint8)
    mn_final = (mn_final / np.max(np.abs(mn_final)) * 127 + 128).astype(np.uint8)
    return mn_final

# --- INTERFAZ ---
st.title("🛡️ Trayector v17: Fuerza Bruta Nokia")
st.write("Transmutando Bach en una trayectoria extendida de Beethoven.")

# El valor maestro de 15 decimales
delta_phi = st.sidebar.number_input(
    "Diferencial de Identidad (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo = st.file_uploader("Subir Bach M0", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Reconstruir Identidad"):
        with st.spinner("Ensamblando Momentum Mn..."):
            resultado = motor_nokia_extensivo(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Soberanía recuperada (Duración extendida).")
            st.audio(buffer, format='audio/wav')
