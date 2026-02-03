"""
Script para capturar audio de YouTube Live Stream en tiempo real
"""
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Importar configuración
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
        # Obtener la URL del stream de audio (sin verificar si es live)
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

def capture_audio_stream(stream_url):
    """Capturar audio del stream y dividirlo en segmentos"""
    print(f"🎙️  Iniciando captura de audio...")
    print(f"   Segmentos de {AUDIO_SEGMENT_DURATION} segundos")
    print(f"\n⏸️  Presiona Ctrl+C para detener\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pattern = os.path.join(AUDIO_CHUNKS_DIR, f"chunk_{timestamp}_%03d.{AUDIO_FORMAT}")
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', stream_url,
        '-f', 'segment',
        '-segment_time', str(AUDIO_SEGMENT_DURATION),
        '-segment_atclocktime', '1',  # Segmentar por tiempo real, no por contenido
        '-reset_timestamps', '1',
        '-ar', str(SAMPLE_RATE),
        '-ac', '1',
        '-c:a', 'pcm_s16le',
        '-avoid_negative_ts', 'make_zero',  # Evitar problemas de timestamps
        output_pattern
    ]
    
    try:
        subprocess.run(ffmpeg_cmd)
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Captura detenida")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    print("=" * 60)
    print("🎯 CAPTURADOR DE AUDIO - CONCEJO DE BELLO")
    print("=" * 60)
    
    setup_directories()
    
    stream_url = get_live_stream_url()
    if not stream_url:
        print("\n⚠️  No hay transmisión en vivo")
        return
    
    capture_audio_stream(stream_url)
    print("\n✓ Proceso finalizado")

if __name__ == "__main__":
    main()