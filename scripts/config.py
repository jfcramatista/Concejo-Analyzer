"""
Configuración del Sistema de Análisis del Concejo
"""
# URL del canal de YouTube del Concejo de Bello
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=Y-IlMeCCtIg"

# Configuración de captura de audio
AUDIO_SEGMENT_DURATION = 300  # Segundos por segmento de audio (5 minutos)
AUDIO_FORMAT = "wav"
SAMPLE_RATE = 16000  # Hz
VIRTUAL_CABLE_ID = 2  # ID actualizado basado en list_audio.py

# Configuración de Whisper
WHISPER_MODEL = "small"  # Opciones: tiny, base, small, medium, large
WHISPER_LANGUAGE = "es"  # Español
WHISPER_DEVICE = "cpu"  # Usar CPU (cambiar a "cuda" si tienes GPU NVIDIA)

# Configuración de Google Sheets
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1BCIqxi0upwqGtqGzWvW5El7PqAjR18pl-fomSUH4dGQ/edit"
CREDENTIALS_FILE = "credentials.json"

# Configuración de Google Docs (Para transcripciones en vivo)
GOOGLE_DOCS_ID = "11pRLz96WSa5hMHU2R7pFiY3OLQIZqsUt_eo2zS1PePw"

# Rutas de salida
OUTPUT_DIR = "output"
AUDIO_CHUNKS_DIR = f"{OUTPUT_DIR}/audio_chunks"
TRANSCRIPTS_DIR = f"{OUTPUT_DIR}/transcripts"
LOGS_DIR = f"{OUTPUT_DIR}/logs"
# Configuración de logging
LOG_LEVEL = "INFO"