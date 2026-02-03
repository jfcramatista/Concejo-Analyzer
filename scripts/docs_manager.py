"""
Gestor de Google Docs para transcripciones en tiempo real
"""
import os
import sys
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import GOOGLE_DOCS_ID, CREDENTIALS_FILE

class DocsManager:
    def __init__(self):
        print("🔗 Conectando a Google Docs...")
        
        # Scopes para Google Docs
        SCOPES = ['https://www.googleapis.com/auth/documents']
        
        # Autenticación
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        self.service = build('docs', 'v1', credentials=creds)
        self.document_id = GOOGLE_DOCS_ID
        
        print(f"✓ Conectado al documento ID: {self.document_id}\n")
    
    def agregar_texto(self, texto):
        """
        Añade texto al final del documento con timestamp
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Formato: [HH:MM:SS] Texto transcrito
        texto_formateado = f"[{timestamp}] {texto}\n"
        
        try:
            # Primero obtenemos el índice final del documento
            doc = self.service.documents().get(documentId=self.document_id).execute()
            end_index = doc.get('body').get('content')[-1].get('endIndex', 1) - 1
            
            # Construimos la solicitud de inserción
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': end_index
                        },
                        'text': texto_formateado
                    }
                }
            ]
            
            # Ejecutamos la inserción
            self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✅ Guardado en Google Docs: [{timestamp}]")
            
        except Exception as e:
            print(f"❌ Error al guardar en Docs: {e}")
