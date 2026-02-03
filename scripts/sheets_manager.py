"""
Gestor de Google Sheets para guardar transcripciones
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *

class SheetsManager:
    def __init__(self):
        """Inicializar conexión con Google Sheets"""
        print("🔗 Conectando a Google Sheets...")
        
        # Configurar credenciales
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        
        # Abrir la hoja
        self.sheet = client.open_by_url(GOOGLE_SHEETS_URL).sheet1
        
        # Configurar encabezados si es la primera vez
        if self.sheet.row_values(1) == []:
            self.sheet.append_row(['Timestamp', 'Fragmento', 'Duración (s)', 'Segmentos', 'Transcripción'])
            print("✓ Encabezados creados")
        
        print(f"✓ Conectado a: {self.sheet.title}\n")
    
    def agregar_transcripcion(self, archivo, duracion, num_segmentos, transcripcion):
        """Agregar una nueva transcripción a la hoja"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row = [
            timestamp,
            archivo,
            f"{duracion:.1f}",
            str(num_segmentos),
            transcripcion
        ]
        
        try:
            self.sheet.append_row(row)
            print(f"✅ Guardado en Google Sheets: {archivo}")
        except Exception as e:
            print(f"❌ Error al guardar en Sheets: {e}")
