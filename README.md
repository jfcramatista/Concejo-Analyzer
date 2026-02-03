# 🎯 Analizador en Tiempo Real - Concejo de Bello
Sistema de captura y transcripción automática de sesiones del Concejo Municipal de Bello.
**Desarrollado para:** Alianza Verde & Pacto Histórico  
**Asesores:** Lauderón (Alianza Verde) y Daniel Quintero Espitia (Pacto Histórico)
---
## 📋 ¿Qué hace este sistema?
1. **Captura** el audio de la transmisión en vivo de YouTube del Concejo
2. **Transcribe** automáticamente lo que se dice en tiempo real
3. **Guarda** las transcripciones en archivos de texto que puedes consultar durante la sesión
---
## 🚀 Cómo usar el sistema
### Antes de la sesión (IMPORTANTE):
1. Asegúrate de tener **conexión a internet estable**
2. Verifica que el Concejo esté transmitiendo en: https://www.youtube.com/@concejobello/live
### Durante la sesión:
1. Abre PowerShell en esta carpeta (`Concejo_Analyzer`)
2. Ejecuta:
   ```powershell
   python run_analyzer.py