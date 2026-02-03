"""
Script para transcribir audio en tiempo real
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from faster_whisper import WhisperModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *
from scripts.sheets_manager import SheetsManager

class AudioTranscriber:
    def __init__(self):
        print(f"🤖 Cargando Whisper '{WHISPER_MODEL}'...")
        self.model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type="int8")
        print(f"✓ Modelo cargado\n")
        
        # Inicializar Google Sheets
        try:
            self.sheets = SheetsManager()
        except Exception as e:
            print(f"⚠️  Error conectando a Google Sheets: {e}")
            print("   Continuando solo con archivo local...\n")
            self.sheets = None
        
        Path(TRANSCRIPTS_DIR).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.transcript_file = os.path.join(TRANSCRIPTS_DIR, f"sesion_{timestamp}.txt")
        
        with open(self.transcript_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"TRANSCRIPCIÓN - CONCEJO DE BELLO\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
        
        print(f"📝 Guardando localmente en: {self.transcript_file}\n")
    
    def transcribe_audio(self, audio_file):
        try:
            print(f"🎧 Transcribiendo: {os.path.basename(audio_file)}")
            
            segments, info = self.model.transcribe(
                audio_file,
                language=WHISPER_LANGUAGE,
                beam_size=5,
                vad_filter=True
            )
            
            transcription = ""
            transcription_plain = ""  # Para Google Sheets (sin timestamps)
            segment_count = 0
            for segment in segments:
                text = segment.text.strip()
                if text:
                    transcription += f"[{segment.start:.1f}s - {segment.end:.1f}s] {text}\n"
                    transcription_plain += f"{text} "
                    segment_count += 1
            
            if transcription:
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Guardar en archivo local
                with open(self.transcript_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- {timestamp} - {os.path.basename(audio_file)} ---\n")
                    f.write(f"Duración: {info.duration:.1f}s | Segmentos: {segment_count}\n")
                    f.write(transcription)
                
                # Guardar en Google Sheets
                if self.sheets:
                    self.sheets.agregar_transcripcion(
                        os.path.basename(audio_file),
                        info.duration,
                        segment_count,
                        transcription_plain.strip()
                    )
                
                print(f"✓ Transcrito ({segment_count} segmentos, {info.duration:.1f}s)\n")
            else:
                print(f"⚠️  Sin contenido de voz detectado\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n")

class AudioFileHandler(FileSystemEventHandler):
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.processed_files = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if file_path.endswith(f'.{AUDIO_FORMAT}') and file_path not in self.processed_files:
            # Esperar a que el archivo termine de escribirse
            print(f"⏳ Detectado: {os.path.basename(file_path)} - Esperando a que termine...")
            
            prev_size = -1
            stable_count = 0
            max_wait = 120  # Máximo 2 minutos de espera
            wait_time = 0
            
            while wait_time < max_wait:
                try:
                    curr_size = os.path.getsize(file_path)
                    
                    if curr_size == prev_size and curr_size > 0:
                        stable_count += 1
                        # Si el tamaño no cambió por 3 verificaciones (6 segundos), está listo
                        if stable_count >= 3:
                            print(f"✓ Archivo listo ({curr_size} bytes)\n")
                            break
                    else:
                        stable_count = 0
                    
                    prev_size = curr_size
                    time.sleep(2)
                    wait_time += 2
                    
                except Exception as e:
                    print(f"⚠️  Error verificando archivo: {e}")
                    time.sleep(2)
                    wait_time += 2
            
            if wait_time >= max_wait:
                print(f"⚠️  Timeout esperando archivo, intentando transcribir de todas formas...\n")
            
            self.processed_files.add(file_path)
            self.transcriber.transcribe_audio(file_path)

import argparse

def main():
    parser = argparse.ArgumentParser(description="Transcriptor de audio del Concejo")
    parser.add_argument("--single-file", help="Ruta de un archivo de audio para transcribir una sola vez")
    args = parser.parse_args()

    print("=" * 80)
    print("🎯 TRANSCRIPTOR - CONCEJO DE BELLO")
    print("=" * 80 + "\n")
    
    transcriber = AudioTranscriber()

    if args.single_file:
        # Modo un solo archivo (ideal para automatización/orquestador)
        if os.path.exists(args.single_file):
            transcriber.transcribe_audio(args.single_file)
        else:
            print(f"❌ Error: El archivo {args.single_file} no existe.")
    else:
        # Modo monitoreo continuo (Watchdog)
        event_handler = AudioFileHandler(transcriber)
        observer = Observer()
        observer.schedule(event_handler, AUDIO_CHUNKS_DIR, recursive=False)
        observer.start()
        
        print(f"👀 Monitoreando: {AUDIO_CHUNKS_DIR}\n")
        print("⏸️  Presiona Ctrl+C para detener\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n⏹️  Detenido por el usuario")
            observer.stop()
        
        observer.join()
        print("\n✓ Transcriptor cerrado correctamente")

if __name__ == "__main__":
    main()