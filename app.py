import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR DE DESENTROPÍA CIEGA (TORRES v18) ---
def motor_ciego_torres(biblioteca_tonos, delta_phi, rate):
    # n! : El sustrato de complejidad (la biblioteca de sonidos puros)
    sustrato = biblioteca_tonos.astype(np.float64)
    n_samples_biblioteca = len(sustrato)
    
    # Mn : El momentum observado (el resultado de 10 segundos)
    duracion_salida = 10 
    total_samples_out = rate * duracion_salida
    m0b_final = np.zeros(total_samples_out, dtype=np.float64)
    
    # RESOLUCIÓN DEL TRAYECTOR
    # El trayector recorre el tiempo de salida y "salta" en la biblioteca
    # basándose puramente en la resonancia del Delta Phi.
    for i in range(total_samples_out):
        t = i / rate
        
        # Esta es la función de búsqueda de identidad:
        # No hay notas escritas, solo la espiral del diferencial de fase.
        # El delta_phi dicta la velocidad de rotación en la biblioteca.
        idx_identidad = int((t * delta_phi * 1000) % n_samples_biblioteca)
        
        m0b_final[i] = sustrato[idx_identidad]

    # Auditoría del Horizonte (8-bit uint8)
    mn_max = np.max(np.abs(m0b_final)) if np.max(np.abs(m0b_final)) > 0 else 1
    return (127 * (m0b_final / mn_max) + 128).astype(np.uint8)

# --- INTERFAZ ---
st.title("🛡️ Auditoría de Identidad: Criba Ciega")
st.write("Sin melodías programadas. Solo el Trayector resolviendo la biblioteca.")

delta_phi = st.sidebar.number_input(
    "Diferencial de Identidad (ΔΦ)", 
    format="%.15f", 
    value=2.721055555555556, 
    step=1e-15
)

archivo_biblioteca = st.file_uploader("Subir Biblioteca de Tonos (M0)", type=["wav"])

if archivo_biblioteca is not None:
    rate, data = wavfile.read(archivo_biblioteca)
    if len(data.shape) > 1: data = data[:, 0]
    
    if st.button("Buscar Identidad Mn"):
        with st.spinner("El Demonio de Laplace está operando..."):
            resultado = motor_ciego_torres(data, delta_phi, rate)
            buffer = io.BytesIO()
            wavfile.write(buffer, rate, resultado)
            st.success("Trayectoria de identidad encontrada.")
            st.audio(buffer, format='audio/wav')
