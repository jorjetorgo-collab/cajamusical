import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- SUSTRATO CROMÁTICO (Abecedario 8-bit) ---
def generar_sustrato_estándar(rate):
    # Do4 a Si4 (Octava central limpia)
    frecuencias = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 
                   369.99, 392.00, 415.30, 440.00, 466.16, 493.88]
    muestras_por_nota = int(rate * 0.4) # Notas más largas para mayor estabilidad
    sustrato = np.array([])
    
    for f in frecuencias:
        t = np.linspace(0, 0.4, muestras_por_nota, endpoint=False)
        # Fuerza bruta: Onda Cuadrada
        nota = np.sign(np.sin(2 * np.pi * f * t))
        sustrato = np.append(sustrato, nota)
    return sustrato

# --- MOTOR TRAYECTOR v24 (Decodificador) ---
def motor_torres_decodificador(delta_phi, rate):
    sustrato = generar_sustrato_estándar(rate)
    n_samples_lib = len(sustrato)
    
    duracion_out = 15 # Aumentamos a 15 segundos para dar espacio
    n_samples_out = int(rate * duracion_out)
    resultado_mn = np.zeros(n_samples_out)
    
    t = np.arange(n_samples_out) / rate
    
    # EL AJUSTE DE DESACELERACIÓN:
    # Reducimos el factor multiplicador del tiempo. 
    # Usamos 'np.floor' para que el trayector se "ancle" a la nota 
    # y no pase volando sobre ella (lo que creaba el efecto de escala rápida).
    paso_humano = 2.0 # Factor de velocidad melódica
    indices = (np.floor(t * delta_phi * paso_humano) * (rate * 0.4)) % n_samples_lib
    
    for i in range(n_samples_out):
        idx = int(indices[i])
        # Aseguramos que el índice no desborde el sustrato
        resultado_mn[i] = sustrato[idx % n_samples_lib]
        
    # Salida 8-bit pura
    mn_max = np.max(np.abs(resultado_mn)) if np.max(np.abs(resultado_mn)) > 0 else 1
    return (127 * (resultado_mn / mn_max) + 128).astype(np.uint8)

# --- INTERFAZ ---
st.set_page_config(page_title="🛡️ Torres v24 - Decodificador", page_icon="🕵️")
st.title("🛡️ Trayector v24: Decodificador Temporal")
st.write("Ralentizando la trayectoria para manifestar la identidad Mn.")

delta_phi = st.sidebar.number_input(
    "ΔΦ (Diferencial de Identidad)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

rate = 22050

if st.button("Decodificar Identidad"):
    with st.spinner("Estabilizando el horizonte de eventos..."):
        resultado = motor_torres_decodificador(delta_phi, rate)
        
        buffer = io.BytesIO()
        wavfile.write(buffer, rate, resultado)
        
        st.success("Trayectoria estabilizada.")
        st.audio(buffer, format='audio/wav')
