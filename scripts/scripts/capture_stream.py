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
    print(f"🔍 Buscando stream en vivo en: {YOUTUBE_CHANNEL_URL}")
    
    try:
        # Obtener la URL del stream de audio
        result = subprocess.run([
            'yt-dlp',
            '-f', 'bestaudio',
            '--get-url',
            YOUTUBE_CHANNEL_URL
        ], capture_output=True, text=True, check=True)
        
        stream_url = result.stdout.strip()
        print(f"✓ Stream encontrado")
        return stream_url
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: No se encontró un stream en vivo activo")
        print(f"   Asegúrate de que el Concejo esté transmitiendo en vivo")
        return None
def capture_audio_stream(stream_url):
    """Capturar audio del stream y dividirlo en segmentos"""
    print(f"🎙️  Iniciando captura de audio...")
    print(f"   Segmentos de {AUDIO_SEGMENT_DURATION} segundos")
    print(f"   Guardando en: {AUDIO_CHUNKS_DIR}")
    print(f"\n⏸️  Presiona Ctrl+C para detener\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pattern = os.path.join(AUDIO_CHUNKS_DIR, f"chunk_{timestamp}_%03d.{AUDIO_FORMAT}")
    
    # Comando FFmpeg para capturar y segmentar
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', stream_url,
        '-f', 'segment',
        '-segment_time', str(AUDIO_SEGMENT_DURATION),
        '-ar', str(SAMPLE_RATE),
        '-ac', '1',  # Mono
        '-c:a', 'pcm_s16le',  # WAV format
        '-reset_timestamps', '1',
        output_pattern
    ]
    
    try:
        subprocess.run(ffmpeg_cmd)
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Captura detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la captura: {e}")
def main():
    """Función principal"""
    print("=" * 60)
    print("🎯 CAPTURADOR DE AUDIO - CONCEJO DE BELLO")
    print("=" * 60)
    
    setup_directories()
    
    stream_url = get_live_stream_url()
    if not stream_url:
        print("\n⚠️  No hay transmisión en vivo en este momento")
        print("   Verifica en: https://www.youtube.com/@concejobello/live")
        return
    
    capture_audio_stream(stream_url)
    
    print("\n✓ Proceso finalizado")
if __name__ == "__main__":
    main()