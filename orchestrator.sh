#!/bin/bash

# =========================================================================
# ORQUESTADOR DE TRANSCRIPCIÓN AUTOMATIZADA - CONCEJO DE BELLO
# =========================================================================

# Cargar variables de entorno/configuración si es necesario
AUDIO_DIR="output/audio_chunks"
TRANSCRIPTS_LOG="output/logs/workflow.log"

mkdir -p "$AUDIO_DIR"
mkdir -p "output/logs"

echo "[$(date)] 🚀 Iniciando Orquestador de Flujo..." | tee -a "$TRANSCRIPTS_LOG"

# Función para limpiar al salir
cleanup() {
    echo -e "\n[$(date)] ⏹️  Deteniendo procesos y limpiando..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# 1. INICIAR LA CAPTURA (Segundo Plano)
# Usamos -segment_atclocktime para que el tiempo sea preciso
# Usamos -segment_wrap para si quisiéramos sobrescribir, pero aquí queremos guardarlos para transcribir
echo "[$(date)] 🎙️  Lanzando Capturador (FFmpeg)..."
python scripts/capture_stream_v3.py &

# 2. BUCLE DE AUTOMATIZACIÓN (Vigilante)
# Este bucle busca archivos .wav terminados que NO estén siendo escritos
echo "[$(date)] 🔍 Vigilante de archivos activado. Esperando fragmentos de 5 min..."

while true; do
    # Buscar archivos .wav en el directorio, excepto los archivos temporales de FFmpeg
    for file in "$AUDIO_DIR"/*.wav; do
        if [ -f "$file" ]; then
            # Si hay más de un archivo, procesamos el más antiguo (el que ya se cerró)
            num_files=$(ls "$AUDIO_DIR"/*.wav | wc -l)
            
            if [ "$num_files" -gt 1 ]; then
                # El archivo actual que FFmpeg está escribiendo suele ser el último alfabéticamente
                current_file=$(ls "$AUDIO_DIR"/*.wav | tail -n 1)
                process_file=$(ls "$AUDIO_DIR"/*.wav | head -n 1)

                if [ "$process_file" != "$current_file" ]; then
                    echo "[$(date)] 🎧 Detectado fragmento listo: $process_file" | tee -a "$TRANSCRIPTS_LOG"
                    
                    # DISPARAR TRANSCRIPCIÖN (Automation)
                    # El script de transcripción ya sabe subir a Google Sheets
                    python scripts/transcribe_realtime.py --single-file "$process_file"
                    
                    # LIMPIEZA (Residuo cero)
                    echo "[$(date)] 🧹 Limpiando archivo de audio procesado..."
                    rm "$process_file"
                fi
            fi
        fi
    done
    sleep 30 # Verificar cada 30 segundos
done
