import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- 1. EL EXTRACTOR CIEGO (ADN) ---
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    # Limpieza de ceros para evitar errores matemáticos
    f_limpias = [f if f > 0 else 0.1 for f in frecuencias]
    cambios = [f_limpias[i+1] / f_limpias[i] for i in range(len(f_limpias)-1)]
    # La firma pura del diferencial
    return np.mean(cambios) * np.std(cambios)

# --- 2. EL MOTOR DE MANIFESTACIÓN ---
def motor_universal(delta_phi, partitura, constante_c, rate=22050):
    duracion = 8  # Tiempo de ejecución
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    for i in range(n_samples):
        t = i / rate
        # Ñ (El Trayector) fluye según el ADN y la Presión (C)
        index = int(np.floor(t * (delta_phi * constante_c))) % len(partitura)
        
        frecuencia = partitura[index]
        if frecuencia > 0.5:
            # Generación de onda cuadrada (Nokia Style)
            incremento = (2 * np.pi * frecuencia) / rate
            fase_acumulada += incremento
            muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        else:
            muestra = 0  # Silencio absoluto para el 0
            
        # El "staccato" o pulso rítmico del sistema
        if (t * (delta_phi * constante_c)) % 1.0 > 0.8: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- 3. INTERFAZ (SISTEMA ABIERTO) ---
st.title("🛡️ Motor v54: Puerto de Inyección")

# Controles de Usuario
c_presion = st.slider("Ajuste de Presión (C):", 5.0, 150.0, 40.0)

# El Puerto de Entrada: Aquí pegas lo que quieras
st.subheader("Inyector de ADN Musical")
input_libre = st.text_area(
    "Escribe las frecuencias separadas por coma (0 para silencio):",
    "261.63, 0, 261.63, 233.08, 261.63, 0, 261.63, 233.08, 261.63, 0, 261.63, 196.0, 207.6"
)

try:
    # Procesamiento de la entrada
    notas = [float(x.strip()) for x in input_libre.split(",")]
    d_phi = extraer_delta_phi(notas)
    
    col1, col2 = st.columns(2)
    col1.metric("ΔΦ (Identidad)", f"{d_phi:.6f}")
    col2.metric("Velocidad (Notas/s)", f"{d_phi * c_presion:.2f}")

    if st.button("🔥 MANIFESTAR ADN"):
        audio_data = motor_universal(d_phi, notas, c_presion)
        buffer = io.BytesIO()
        wavfile.write(buffer, 22050, audio_data)
        st.audio(buffer, format='audio/wav')
        
    st.info("💡 Tip: Para baladas baja C a 20. Para ritmos agresivos sube C a 60.")

except Exception as e:
    st.warning("Esperando entrada de ADN válida...")
