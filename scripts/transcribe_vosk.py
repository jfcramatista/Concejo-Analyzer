import os
import sys
import queue
import json
import pyaudio
import threading
from vosk import Model, KaldiRecognizer
from datetime import datetime

# Importar configuración
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *
from scripts.docs_manager import DocsManager

def main():
    print("=" * 60)
    print("🟢 MATRIX STREAMING - VOSK LOCAL + GOOGLE DOCS")
    print("=" * 60)

    if not os.path.exists("model"):
        print("❌ Error: No se encuentra la carpeta 'model'.")
        return

    # 1. Inicializar Google Docs (Opcional, si falla seguimos solo local)
    docs_manager = None
    try:
        docs_manager = DocsManager()
        print("📝 Conectado a Google Docs para subida en segundo plano.")
    except Exception as e:
        print(f"⚠️  No se pudo conectar a Docs ({e}). Solo modo local.")

    # 2. Cola de subida (Para no bloquear el audio)
    upload_queue = queue.Queue()

    # Función del empleado que sube los textos (Corre en paralelo)
    def upload_worker():
        while True:
            text_to_upload = upload_queue.get()
            if docs_manager:
                try:
                    docs_manager.agregar_texto(text_to_upload)
                except Exception as e:
                    print(f"\n⚠️ Error subiendo a Docs: {e}")
            upload_queue.task_done()

    # Iniciar el hilo del escriba
    if docs_manager:
        threading.Thread(target=upload_worker, daemon=True).start()

    # 3. Cargar modelo Vosk
    print("🧠 Cargando red neuronal...")
    model = Model("model")
    rec = KaldiRecognizer(model, 16000)
    
    # 4. Cola de audio (Buffer)
    audio_queue = queue.Queue()

    def callback(in_data, frame_count, time_info, status):
        audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    # 5. Conectar al Cable Virtual
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
        print("🚀 ¡ESCUCHANDO! (Ctrl+C para salir)\n")
        
        last_partial_len = 0
        
        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                # Frase completa
                res = json.loads(rec.Result())
                if res['text']:
                    # Limpiar línea actual
                    print(" " * (last_partial_len + 5), end="\r")
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    texto_final = res['text']
                    print(f"[{timestamp}] ✅ {texto_final}")
                    
                    # ENVIAR AL ESCRIBA (No bloquea)
                    upload_queue.put(texto_final)
                    
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
