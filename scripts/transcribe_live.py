# -*- coding: utf-8 -*-
"""
SISTEMA DE TRANSCRIPCIÓN LIVE - CONCEJO DE BELLO
Estrategia: Motor de Google Speech Recognition (Rápido y preciso)
"""
import os
import sys
import time
from datetime import datetime
import speech_recognition as sr

# Importar configuración y gestores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *

def main():
    print("=" * 60)
    print("⚡ TRANSCRIPCIÓN TERMINAL - ALTA VELOCIDAD")
    print("=" * 60)

    # 1. Configurar el "Oído"
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.5  # <--- CLAVE: Corte rápido para efecto "subtítulo"
    
    # 2. Preparar el micrófono
    try:
        source = sr.Microphone(device_index=VIRTUAL_CABLE_ID)
        with source:
            print("⏳ Calibrando silencio (1s)...")
            r.adjust_for_ambient_noise(source, duration=1)
    except Exception as e:
        print(f"❌ Error con ID {VIRTUAL_CABLE_ID}: {e}")
        return

    print("🚀 ¡ESCUCHANDO! Habla o reproduce el video...")
    print("⏸️  Ctrl+C para salir.\n")

    # Callback ultrarrapido
    def callback(recognizer, audio):
        try:
            # Reconocimiento rápido de Google
            texto = recognizer.recognize_google(audio, language="es-ES")
            
            # Imprimir al instante limpio
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] >> {texto}")
            
        except sr.UnknownValueError:
            pass 
        except sr.RequestError:
            print("⚠️ Red lenta...")
        except Exception as e:
            print(f"Error: {e}")

    # Escucha en background
    stop_listening = r.listen_in_background(source, callback, phrase_time_limit=10)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_listening(wait_for_stop=False)
        print("\n⏹️ Fin.")


if __name__ == "__main__":
    main()
