import os
import sys
import queue
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from datetime import datetime

# Importar configuración
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *

def main():
    print("=" * 60)
    print("🟢 MATRIX STREAMING - VOSK LOCAL")
    print("=" * 60)

    if not os.path.exists("model"):
        print("❌ Error: No se encuentra la carpeta 'model'.")
        print("   Ejecuta primero: python scripts/install_vosk_model.py")
        return

    # 1. Cargar modelo (Es muy rápido)
    print("🧠 Cargando red neuronal...")
    model = Model("model")
    rec = KaldiRecognizer(model, 16000)
    
    # 2. Cola de audio (Buffer)
    q = queue.Queue()

    def callback(in_data, frame_count, time_info, status):
        q.put(in_data)
        return (None, pyaudio.paContinue)

    # 3. Conectar al Cable Virtual
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        input_device_index=VIRTUAL_CABLE_ID,
                        frames_per_buffer=4000,
                        stream_callback=callback)
                        
        print(f"🎧 Conectado al ID: {VIRTUAL_CABLE_ID}")
        stream.start_stream()
        print("🚀 ¡ESCUCHANDO EN FLUJO CONTINUO! (Ctrl+C para salir)\n")
        
        last_partial_len = 0
        
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                # Frase completa
                res = json.loads(rec.Result())
                if res['text']:
                    # Limpiar línea actual
                    print(" " * (last_partial_len + 5), end="\r")
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] ✅ {res['text']}")
                    last_partial_len = 0
            else:
                # Resultado parcial (Streaming)
                partial = json.loads(rec.PartialResult())
                if partial['partial']:
                    text = partial['partial']
                    
                    # Manejo visual: Si es muy largo, mostrar solo el final "..."
                    # Asumimos ancho de consola de 100 caracteres aprox
                    max_width = 80
                    display_text = text
                    if len(text) > max_width:
                        display_text = "..." + text[-(max_width-3):]
                    
                    # Imprimir sobreescribiendo
                    # Rellenamos con espacios para borrar basura anterior si la frase se encoge
                    print_str = f">> {display_text}"
                    params = print_str.ljust(last_partial_len) 
                    
                    print(f"\r{params}", end="", flush=True)
                    last_partial_len = len(params)

    except KeyboardInterrupt:
        print("\n\n⏹️ Deteniendo...")
        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
