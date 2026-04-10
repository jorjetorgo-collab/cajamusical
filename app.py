import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# --- MOTOR v52 (Sintonía Fina) ---
def extraer_delta_phi(frecuencias):
    if len(frecuencias) < 2: return 1.0
    cambios = [frecuencias[i+1] / frecuencias[i] for i in range(len(frecuencias)-1)]
    return np.mean(cambios) * np.std(cambios)

def motor_universal_v52(delta_phi, partitura, rate=22050):
    duracion = 12 
    n_samples = int(rate * duracion)
    resultado = np.zeros(n_samples)
    fase_acumulada = 0.0
    
    # NUEVA CONSTANTE DE EQUILIBRIO (Más solemne)
    C_ESTETICA = 25.0 
    
    for i in range(n_samples):
        t = i / rate
        ñ = int(np.floor(t * (delta_phi * C_ESTETICA))) % len(partitura)
        
        frecuencia = partitura[ñ]
        incremento = (2 * np.pi * frecuencia) / rate
        fase_acumulada += incremento
        
        muestra = 1.0 if np.sin(fase_acumulada) > 0 else -1.0
        # Silencio rítmico más largo para dar "aire"
        if (t * (delta_phi * C_ESTETICA)) % 1.0 > 0.7: muestra = 0
        resultado[i] = muestra
            
    return (127 * resultado + 128).astype(np.uint8)

# --- PRUEBA DE LA PANTERA (ADN CON PAUSAS) ---
# He añadido frecuencias bajas (0.1) que actúan como "anclas" de tiempo
pantera_adn = "138, 146, 0.1, 155, 164, 0.1, 138, 146, 155, 164, 207, 196, 164"

# ... (Interfaz de Streamlit igual que antes)
