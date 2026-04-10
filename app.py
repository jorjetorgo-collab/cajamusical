import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE GENERACIÓN DE SUSTRATO PURO ---
def generar_sustrato_nokia_puro(rate):
    # Generamos las 12 notas de la escala cromática (Do a Si)
    # Frecuencias base (Octava 4)
    frecuencias = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 
                   369.99, 392.00, 415.30, 440.00, 466.16, 493.88]
    duracion_nota = 0.5
    sustrato_completo = np.array([])
    
    for f in frecuencias:
        t = np.linspace(0, duracion_nota, int(rate * duracion_nota), endpoint=False)
        # Onda cuadrada pura (Fuerza bruta 8-bit)
        nota = np.sign(np.sin(2 * np.pi * f * t))
        sustrato_completo = np.append(sustrato_completo, nota)
        
    return sustrato_completo

# --- MOTOR DE TRAYECTORIA v22 ---
def motor_torres_puro(delta_phi, rate):
    # 1. Creamos el sustrato M0 internamente (Sin ruidos externos)
    sustrato = generar_sustrato_nokia_puro(rate)
    n_samples_lib = len(sustrato)
    
    # 2. Mn: El momentum observado (10 segundos)
    duracion_out = 10
    n_samples_out = int(rate * duracion_out)
    resultado_mn = np.zeros(n_samples_out)
    
    # 3. EL TRAYECTOR (N): Escaneo sobre la escala pura
    t = np.arange(n_samples_out) / rate
    
    # Aplicamos el diferencial de fase para decidir el "paso"
    # El delta_phi ahora sintoniza directamente sobre la escala cromática
    pasos = (np.floor(t * delta_phi * 5.5) * (rate * 0.5)) % n_samples_lib
    
    for i in range(n_samples_out):
        idx = int(pasos[i])
        resultado_mn[i] = sustrato[idx]
        
    # 4. AUDITORÍA DEL HORIZONTE
    mn_max = np.max(np.abs(resultado_mn)) if np.max(np.abs(resultado_mn)) > 0 else 1
    return (127 * (resultado_mn / mn_max) + 128).astype(np.uint8)

# --- INTERFAZ ---
st.set_page_config(page_title="🛡️ Torres v22 - Generador de Realidad", page_icon="🎹")
st.title("🛡️ Trayector v22: Reconstrucción desde Sustrato Puro")
st.write("Generando un abecedario de 8 bits para extraer a Beethoven.")

delta_phi = st.sidebar.number_input(
    "Diferencial de Fase (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

rate = 22050 # Frecuencia de muestreo estándar para 8-bit

if st.button("Manifestar Identidad Pura"):
    with st.spinner("Fabricando sustrato y sintonizando Mn..."):
        # Ya no pedimos archivo, generamos la realidad aquí:
        resultado = motor_torres_puro(delta_phi, rate)
        
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, resultado)
        
        st.success("Igualación final completada sobre sustrato de control.")
        st.audio(buffer, format='audio/wav')
        
        st.download_button(
            label="Descargar Mn Pura",
            data=buffer.getvalue(),
            file_name="beethoven_puro_8bit.wav",
            mime="audio/wav"
        )

st.info("Esta versión no requiere archivos externos. El ΔΦ busca la melodía en una escala cromática pura generada por el código.")
