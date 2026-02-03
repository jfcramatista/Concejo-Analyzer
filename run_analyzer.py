"""
Script Principal - Analizador del Concejo en Tiempo Real
Ejecuta este script para iniciar la captura y transcripción
"""
import subprocess
import sys
import time
from pathlib import Path

def print_banner():
    """Mostrar banner del sistema"""
    print("\n" + "=" * 80)
    print("🎯 ANALIZADOR EN TIEMPO REAL - CONCEJO DE BELLO")
    print("=" * 80)
    print("\nSistema de captura y transcripción automática de sesiones")
    print("Desarrollado para: Alianza Verde & Pacto Histórico")
    print("=" * 80 + "\n")

def check_dependencies():
    """Verificar que las herramientas necesarias estén instaladas"""
    print("🔍 Verificando dependencias...\n")
    
    dependencies = {
        'yt-dlp': ['yt-dlp', '--version'],
        'ffmpeg': ['ffmpeg', '-version'],
        'Python faster-whisper': [sys.executable, '-c', 'import faster_whisper']
    }
    
    all_ok = True
    for name, cmd in dependencies.items():
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"  ✓ {name}")
        except:
            print(f"  ❌ {name} - NO INSTALADO")
            all_ok = False
    
    print()
    return all_ok

def main():
    """Función principal"""
    print_banner()
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ Faltan dependencias. Por favor instala los requisitos faltantes.")
        return
    
    print("✓ Todas las dependencias están instaladas\n")
    print("=" * 80)
    print("INSTRUCCIONES:")
    print("=" * 80)
    print("\n1. Este script abrirá DOS ventanas de terminal:")
    print("   - Terminal 1: Captura de audio del stream")
    print("   - Terminal 2: Transcripción en tiempo real")
    print("\n2. Ambas ventanas deben permanecer abiertas durante la sesión")
    print("\n3. Para detener el sistema: Presiona Ctrl+C en ambas ventanas")
    print("\n4. Las transcripciones se guardan en: output/transcripts/")
    print("\n" + "=" * 80)
    
    input("\n⏸️  Presiona ENTER para iniciar el sistema...")
    
    print("\n🚀 Iniciando sistema...\n")
    
    # Rutas de los scripts
    capture_script = Path("scripts/capture_stream.py")
    capture_script_v2 = Path("scripts/capture_stream_v2.py")
    transcribe_script = Path("scripts/transcribe_realtime.py")
    
    # Verificar que existan los scripts
    if not capture_script_v2.exists():
        print(f"❌ Error: No se encuentra {capture_script_v2}")
        return
    
    if not transcribe_script.exists():
        print(f"❌ Error: No se encuentra {transcribe_script}")
        return
    
    print("📝 Paso 1: Iniciando transcriptor (espera a que cargue el modelo)...")
    
    # Iniciar transcriptor en nueva ventana
    transcribe_cmd = f'start "Transcriptor - Concejo" cmd /k "python {transcribe_script}"'
    subprocess.Popen(transcribe_cmd, shell=True)
    
    print("⏳ Esperando 5 segundos para que el modelo Whisper cargue...\n")
    time.sleep(5)
    
    print("🎙️  Paso 2: Iniciando capturador de audio (V2 - Captura continua)...")
    
    # Iniciar capturador V2 en nueva ventana
    capture_cmd = f'start "Capturador - Concejo" cmd /k "python {capture_script_v2}"'
    subprocess.Popen(capture_cmd, shell=True)
    
    print("\n" + "=" * 80)
    print("✓ SISTEMA INICIADO")
    print("=" * 80)
    print("\n📺 Verifica que las dos ventanas se hayan abierto:")
    print("   1. Ventana 'Capturador - Concejo'")
    print("   2. Ventana 'Transcriptor - Concejo'")
    print("\n📄 Las transcripciones aparecerán en: output/transcripts/")
    print("\n⚠️  IMPORTANTE: No cierres las ventanas hasta que termine la sesión")
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Proceso interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")