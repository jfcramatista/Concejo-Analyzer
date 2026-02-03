"""
Script para transcribir audio en tiempo real usando Whisper
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from faster_whisper import WhisperModel
# Importar configuración
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *
class AudioTranscriber:
    """Clase para manejar la transcripción de audio"""
    
    def __init__(self):
        print(f"🤖 Cargando modelo Whisper '{WHISPER_MODEL}'...")
        self.model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type="int8"  # Optimización para CPU
        )
        print(f"✓ Modelo cargado")
        
        # Crear directorio de transcripciones
        Path(TRANSCRIPTS_DIR).mkdir(parents=True, exist_ok=True)
        
        # Archivo de transcripción completa
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.transcript_file = os.path.join(TRANSCRIPTS_DIR, f"sesion_{timestamp}.txt")
        
        # Crear archivo con encabezado
        with open(self.transcript_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"TRANSCRIPCIÓN - CONCEJO DE BELLO\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
        
        print(f"📝 Transcripciones se guardarán en: {self.transcript_file}")
    
    def transcribe_audio(self, audio_file):
        """Transcribir un archivo de audio"""
        try:
            print(f"\n🎧 Transcribiendo: {os.path.basename(audio_file)}")
            
            segments, info = self.model.transcribe(
                audio_file,
                language=WHISPER_LANGUAGE,
                beam_size=5,
                vad_filter=True  # Filtro de detección de voz
            )
            
            # Procesar segmentos
            transcription = ""
            for segment in segments:
                text = segment.text.strip()
                if text:
                    transcription += f"[{segment.start:.1f}s - {segment.end:.1f}s] {text}\n"
            
            if transcription:
                # Guardar en archivo
                timestamp = datetime.now().strftime("%H:%M:%S")
                with open(self.transcript_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- {timestamp} ---\n")
                    f.write(transcription)
                
                print(f"✓ Transcrito: {len(transcription)} caracteres")
                print(f"📄 Contenido:\n{transcription}")
            else:
                print(f"⚠️  No se detectó voz en este segmento")
            
        except Exception as e:
            print(f"❌ Error al transcribir {audio_file}: {e}")
class AudioFileHandler(FileSystemEventHandler):
    """Manejador de eventos para nuevos archivos de audio"""
    
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.processed_files = set()
    
    def on_created(self, event):
        """Cuando se crea un nuevo archivo"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # Verificar que sea un archivo de audio y no lo hayamos procesado
        if file_path.endswith(f'.{AUDIO_FORMAT}') and file_path not in self.processed_files:
            # Esperar a que el archivo termine de escribirse
            time.sleep(2)
            
            # Marcar como procesado
            self.processed_files.add(file_path)
            
            # Transcribir
            self.transcriber.transcribe_audio(file_path)
def main():
    """Función principal"""
    print("=" * 80)
    print("🎯 TRANSCRIPTOR EN TIEMPO REAL - CONCEJO DE BELLO")
    print("=" * 80)
    
    # Inicializar transcriptor
    transcriber = AudioTranscriber()
    
    # Configurar observador de archivos
    event_handler = AudioFileHandler(transcriber)
    observer = Observer()
    observer.schedule(event_handler, AUDIO_CHUNKS_DIR, recursive=False)
    observer.start()
    
    print(f"\n👀 Monitoreando carpeta: {AUDIO_CHUNKS_DIR}")
    print(f"⏸️  Presiona Ctrl+C para detener\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Transcriptor detenido por el usuario")
        observer.stop()
    
    observer.join()
    print(f"\n✓ Proceso finalizado")
if __name__ == "__main__":
    main()