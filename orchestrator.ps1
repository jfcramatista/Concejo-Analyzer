# =========================================================================
# ORQUESTADOR DE FLUJO (POWERSHELL) - CONCEJO DE BELLO
# =========================================================================

$AUDIO_DIR = "output/audio_chunks"
$LOGS_DIR = "output/logs"
$TRANSCRIPTS_LOG = "$LOGS_DIR/workflow.log"

# Asegurar que los directorios existan
if (!(Test-Path $AUDIO_DIR)) { New-Item -ItemType Directory -Path $AUDIO_DIR }
if (!(Test-Path $LOGS_DIR)) { New-Item -ItemType Directory -Path $LOGS_DIR }

Write-Host "[$(Get-Date)] >>> Iniciando Orquestador de Flujo..." -ForegroundColor Cyan

# 1. INICIAR LA CAPTURA EN SEGUNDO PLANO
Write-Host "[$(Get-Date)] [CAPTURA] Lanzando Capturador (V3)..." -ForegroundColor Yellow
$captureProcess = Start-Process python -ArgumentList "scripts/capture_stream_v3.py" -PassThru -WindowStyle Normal

# 2. BUCLE DE AUTOMATIZACIÓN
Write-Host "[$(Get-Date)] [SISTEMA] Vigilante activado. Esperando fragmentos..." -ForegroundColor Green

try {
    while ($true) {
        # Obtener archivos WAV, ordenados por fecha
        $files = Get-ChildItem -Path "$AUDIO_DIR/*.wav" | Sort-Object LastWriteTime
        
        if ($files.Count -gt 1) {
            # El último archivo es el que FFmpeg está escribiendo actualmente
            # Tomamos todos menos el último para procesar
            $filesToProcess = $files | Select-Object -First ($files.Count - 1)
            
            foreach ($file in $filesToProcess) {
                Write-Host "[$(Get-Date)] [TRANSCRIPCION] Procesando: $($file.Name)" -ForegroundColor Cyan
                
                # Ejecutar transcripción (Síncrono para no saturar la CPU)
                python scripts/transcribe_realtime.py --single-file "$($file.FullName)"
                
                # LIMPIEZA (DESACTIVADA PARA VERIFICACIÓN)
                Write-Host "[$(Get-Date)] [SISTEMA] El archivo se mantendrá para verificación: $($file.Name)" -ForegroundColor Gray
                # Remove-Item $file.FullName -Force
            }
        }
        
        Start-Sleep -Seconds 15 # Verificar cada 15 segundos
    }
}
finally {
    # Al detener con Ctrl+C, cerrar el proceso de captura
    Write-Host "`n[$(Get-Date)] [FIN] Deteniendo procesos..." -ForegroundColor Red
    if ($null -ne $captureProcess) {
        Stop-Process -Id $captureProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
