# -*- coding: utf-8 -*-
"""
Script mejorado para capturar audio de YouTube Live Stream
Captura continua + corte manual cada 5 minutos usando FFmpeg directamente
"""
import subprocess
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Fix para emojis en Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *

def setup_directories():
    """Crear directorios de salida si no existen"""
    Path(AUDIO_CHUNKS_DIR).mkdir(parents=True, exist_ok=True)
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    print(f"✓ Directorios configurados")

def get_live_stream_url():
    """Obtener URL del stream en vivo usando yt-dlp"""
    print(f"🔍 Buscando stream en: {YOUTUBE_CHANNEL_URL}")
    
    try:
        result = subprocess.run([
            'yt-dlp',
            '-f', 'bestaudio/best',
            '--get-url',
            YOUTUBE_CHANNEL_URL
        ], capture_output=True, text=True, check=True)
        
        stream_url = result.stdout.strip()
        print(f"✓ Stream encontrado")
        return stream_url
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: No se pudo obtener el stream")
        print(f"   Detalles: {e.stderr if e.stderr else 'Sin detalles'}")
        return None

class ContinuousCapture:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.running = False
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_audio = os.path.join(AUDIO_CHUNKS_DIR, f"temp_capture_{self.timestamp}.wav")
        self.chunk_counter = 0
        self.start_time = time.time()
        
    def start_capture(self):
        """Iniciar captura continua en un thread separado"""
        self.running = True
        
        # Comando FFmpeg para captura continua
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', self.stream_url,
            '-ar', str(SAMPLE_RATE),
            '-ac', '1',
            '-c:a', 'pcm_s16le',
            '-f', 'wav',
            '-y',  # Sobrescribir
            self.temp_audio
        ]
        
        print(f"🎙️  Iniciando captura continua...")
        print(f"   Archivo temporal: {self.temp_audio}")
        print(f"   Fragmentos cada {AUDIO_SEGMENT_DURATION} segundos\n")
        
        # Ejecutar FFmpeg en background
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Iniciar thread de corte
        self.cutter_thread = threading.Thread(target=self.cut_chunks)
        self.cutter_thread.start()
        
    def cut_chunks(self):
        """Cortar fragmentos cada 5 minutos usando FFmpeg"""
        print(f"✂️  Iniciando cortador de fragmentos...")
        print(f"⏸️  Presiona Ctrl+C para detener\n")
        
        last_cut_time = 0
        
        while self.running:
            time.sleep(10)  # Verificar cada 10 segundos
            
            try:
                # Calcular tiempo transcurrido
                elapsed = time.time() - self.start_time
                
                # Si han pasado 5 minutos desde el último corte
                if elapsed - last_cut_time >= AUDIO_SEGMENT_DURATION:
                    # Esperar a que el archivo exista
                    if not os.path.exists(self.temp_audio):
                        continue
                    
                    file_size = os.path.getsize(self.temp_audio)
                    if file_size < 10000:  # Menos de 10KB
                        print(f"⏳ Esperando más audio...")
                        continue
                    
                    # Nombre del fragmento
                    chunk_filename = f"chunk_{self.timestamp}_{self.chunk_counter:03d}.{AUDIO_FORMAT}"
                    chunk_path = os.path.join(AUDIO_CHUNKS_DIR, chunk_filename)
                    
                    # Copiar el archivo temporal al fragmento usando FFmpeg
                    # Extraer solo los últimos AUDIO_SEGMENT_DURATION segundos
                    cut_cmd = [
                        'ffmpeg',
                        '-i', self.temp_audio,
                        '-ss', str(last_cut_time),
                        '-t', str(AUDIO_SEGMENT_DURATION),
                        '-c', 'copy',
                        '-y',
                        chunk_path
                    ]
                    
                    result = subprocess.run(cut_cmd, capture_output=True)
                    
                    if result.returncode == 0 and os.path.exists(chunk_path):
                        chunk_size = os.path.getsize(chunk_path)
                        print(f"✓ Fragmento guardado: {chunk_filename} ({chunk_size/1024:.1f}KB)")
                        
                        last_cut_time = elapsed
                        self.chunk_counter += 1
                    else:
                        print(f"⚠️  Error creando fragmento")
                
            except Exception as e:
                print(f"⚠️  Error cortando fragmento: {e}")
                time.sleep(5)
    
    def stop(self):
        """Detener la captura"""
        print(f"\n⏹️  Deteniendo captura...")
        self.running = False
        
        if hasattr(self, 'ffmpeg_process'):
            self.ffmpeg_process.terminate()
            self.ffmpeg_process.wait()
        
        if hasattr(self, 'cutter_thread'):
            self.cutter_thread.join(timeout=10)
        
        # Limpiar archivo temporal
        if os.path.exists(self.temp_audio):
            try:
                os.remove(self.temp_audio)
                print(f"✓ Archivo temporal eliminado")
            except:
                pass
        
        print(f"✓ Captura detenida. Total de fragmentos: {self.chunk_counter}")

def main():
    print("=" * 60)
    print("🎯 CAPTURADOR DE AUDIO V2 - CONCEJO DE BELLO")
    print("=" * 60)
    
    setup_directories()
    
    stream_url = get_live_stream_url()
    if not stream_url:
        print("\n⚠️  No hay transmisión en vivo")
        return
    
    capture = ContinuousCapture(stream_url)
    
    try:
        capture.start_capture()
        
        # Mantener el proceso vivo
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        capture.stop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        capture.stop()
    
    print("\n✓ Proceso finalizado")

if __name__ == "__main__":
    main()
