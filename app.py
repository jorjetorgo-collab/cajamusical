import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- BIBLIOTECA DE SONIDOS 8-BIT (SISTEMA CERRADO) ---
def generar_nota_8bit(frecuencia, duracion, rate, sustrato_fragmento):
    t = np.linspace(0, duracion, int(rate * duracion), endpoint=False)
    # Generamos la base del Nokia (Onda cuadrada para fuerza bruta)
    onda_pura = np.sign(np.sin(2 * np.pi * frecuencia * t))
    
    # Aplicamos el sustrato (Bach) como modulador de identidad
    # Esto "ensucia" la onda pura con la desentropía de tu archivo
    if len(sustrato_fragmento) > len(onda_pura):
        modulador = sustrato_fragmento[:len(onda_pura)]
    else:
        modulador = np.pad(sustrato_fragmento, (0, len(onda_pura)-len(sustrato_fragmento)))
    
    return onda_pura * (modulador / np.max(np.abs(modulador)) if np.max(np.abs(modulador)) > 0 else 1)

def motor_nokia_torres(sustrato_audio, delta_phi, rate):
    # 1. DEFINICIÓN DE LA MELODÍA Mn (Para Elisa)
    # Frecuencias de las notas principales
    E5, Dsh5, B4, D5, C5, A4 = 659.25, 622.25, 493.88, 587.33, 523.25, 440.0
    
    # La secuencia de la identidad de Beethoven
    melodia = [
        (E5, 0.2), (Dsh5, 0.2), (E5, 0.2), (Dsh5, 0.2), (E5, 0.2), 
        (B4, 0.2), (D5, 0.2), (C5, 0.2), (A4, 0.4)
    ]
    
    resultado_final = np.array([], dtype=np.float32)
    
    # 2. EL TRAYECTOR (N) RECONSTRUYE DESDE EL DICCIONARIO
    for i, (frec, dur) in enumerate(melodia):
        # Usamos el delta_phi para saltar a un punto distinto del sustrato de Bach
        # para cada nota. Así Bach pierde su orden y cede su identidad a Beethoven.
        punto_muestreo = int((i * delta_phi * rate) % (len(sustrato_audio) - int(rate * 0.4)))
        fragmento_bach = sustrato_audio[punto_muestreo : punto_muestreo + int(rate * dur)]
        
        nota = generar_nota_8bit(frec, dur, rate, fragmento_bach)
        resultado_final = np.append(resultado_final, nota)
    
    # 3. NORMALIZACIÓN 8-BIT (Auditoría del Horizonte)
    resultado_final = (resultado_final / np.max(np.abs(resultado_final)) * 127 + 128).astype(np.uint8)
    return resultado_final

# --- INTERFAZ ---
st.title("🛡️ Reconstructor de Identidad v16")
st.write("Usando Bach como 'biblioteca de átomos' para reconstruir Para Elisa (8-bit)")

delta_phi = st.sidebar.number_input("ΔΦ (15 decimales)", format="%.15f", value=2.721055555555556)

archivo = st.file_uploader("Subir Bach (Sustrato de átomos)", type=["wav"])

if archivo is not None:
    rate, data = wavfile.read(archivo)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Reconstrucción Forzada"):
        with st.spinner("Extrayendo átomos de Bach para Beethoven..."):
            # Aquí ocurre la magia: Bach ya no dicta el tiempo, solo presta sus bits
            resultado = motor_nokia_torres(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Soberanía recuperada: Para Elisa 8-bit manifestada.")
            st.audio(buffer, format='audio/wav')
