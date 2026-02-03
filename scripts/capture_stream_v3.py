# -*- coding: utf-8 -*-
"""
Script de captura V3 - Descarga completa del stream y corte posterior
"""
import subprocess
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *

def setup_directories():
    """Crear directorios de salida"""
    Path(AUDIO_CHUNKS_DIR).mkdir(parents=True, exist_ok=True)
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    print("OK Directorios configurados")

def get_live_stream_url():
    """Obtener URL del stream"""
    print(f"Buscando stream en: {YOUTUBE_CHANNEL_URL}")
    
    try:
        result = subprocess.run([
            'yt-dlp',
            '-f', 'bestaudio/best',
            '--get-url',
            YOUTUBE_CHANNEL_URL
        ], capture_output=True, text=True, check=True)
        
        stream_url = result.stdout.strip()
        print("OK Stream encontrado")
        return stream_url
    
    except subprocess.CalledProcessError as e:
        print(f"ERROR: No se pudo obtener el stream")
        return None

def capture_audio_stream(stream_url):
    """Capturar audio con segmentación forzada"""
    print(f"Iniciando captura de audio...")
    print(f"Segmentos de {AUDIO_SEGMENT_DURATION} segundos")
    print(f"Presiona Ctrl+C para detener\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pattern = os.path.join(AUDIO_CHUNKS_DIR, f"chunk_{timestamp}_%03d.{AUDIO_FORMAT}")
    
    # Comando FFmpeg con force_key_frames para forzar cortes exactos
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', stream_url,
        '-f', 'segment',
        '-segment_time', str(AUDIO_SEGMENT_DURATION),
        '-force_key_frames', f'expr:gte(t,n_forced*{AUDIO_SEGMENT_DURATION})',
        '-ar', str(SAMPLE_RATE),
        '-ac', '1',
        '-c:a', 'pcm_s16le',
        '-reset_timestamps', '1',
        '-break_non_keyframes', '1',
        output_pattern
    ]
    
    try:
        subprocess.run(ffmpeg_cmd)
    except KeyboardInterrupt:
        print(f"\n\nCaptura detenida")
    except Exception as e:
        print(f"\nERROR: {e}")

def main():
    print("=" * 60)
    print("CAPTURADOR DE AUDIO V3 - CONCEJO DE BELLO")
    print("=" * 60)
    
    setup_directories()
    
    stream_url = get_live_stream_url()
    if not stream_url:
        print("\nNo hay transmision en vivo")
        return
    
    capture_audio_stream(stream_url)
    print("\nProceso finalizado")

if __name__ == "__main__":
    main()
