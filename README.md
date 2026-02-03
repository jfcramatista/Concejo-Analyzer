# 🎙️ Concejo Analyzer: Sistema de Transcripción en Tiempo Real (Matrix Stream)

> Un sistema de inteligencia artificial diseñado para transcribir sesiones políticas, reuniones y fluxos de audio en tiempo real, operando localmente para máxima velocidad y sincronizando actas automáticamente en la nube.

---

## 🧠 Arquitectura "Cerebro Dividido"

Este proyecto utiliza una arquitectura de procesamiento concurrente para garantizar **cero pérdida de audio** y **velocidad instantánea**.

### 1. El Oído (Vosk Engine - Local) 👂
- **Tecnología:** [Vosk](https://alphacephei.com/vosk/) (Modelos de lenguaje offline).
- **Función:** Escucha el flujo de audio del sistema (vía Cable Virtual) y transcribe fonéticamente en tiempo real.
- **Ventaja:** No depende de internet ni de APIs lentas. Funciona a la velocidad de la luz en tu terminal.

### 2. El Escriba Fantasma (Google Docs Worker) ✍️
- **Tecnología:** Google Docs API + Python Threading.
- **Función:** Un hilo secundario que toma las frases transcritas y las "inyecta" silenciosamente en un documento de Google Docs compartido.
- **Ventaja:** Funciona en segundo plano (asíncrono). Si el internet falla, la transcripción local NO se detiene.

---

## 🛠️ Requisitos Previos

### 1. El Puente de Audio (Driver)
Para que el bot "escuche" lo que suena en tu PC (YouTube, Meet, Zoom), necesitas un **Cable Virtual**.
1. Descarga e instala **VB-CABLE Driver** desde [vb-audio.com](https://vb-audio.com/Cable/).
2. Reinicia tu PC.
3. En la configuración de sonido de Windows, establece la Salida en **"CABLE Input"**.

### 2. Entorno Python
```bash
pip install -r requirements.txt
```

### 3. Credenciales de Google
- Necesitas un archivo `credentials.json` en la raíz del proyecto (Service Account de Google Cloud).
- Habilita la API de Google Docs en tu consola de Google Cloud.
- Comparte tu documento de Google Docs con el email del bot (`tu-bot@proyecto.iam.gserviceaccount.com`) dándole permisos de **Editor**.

---

## 🚀 Instalación y Uso

### 1. Instalar el Modelo Neuronal (Solo la primera vez)
El bot necesita un "cerebro" para entender español. Ejecuta este script para descargarlo automáticamente (40MB):
```powershell
python scripts/install_vosk_model.py
```

### 2. Configuración
Edita `scripts/config.py`:
- **GOOGLE_DOCS_ID:** Pega el ID de tu documento de Google Docs (está en la URL).
- **VIRTUAL_CABLE_ID:** (Opcional) Si el script no escucha, usa `scripts/list_audio.py` para encontrar el ID correcto de tu Cable Virtual.

### 3. ¡Iniciar la Matrix!
```powershell
python scripts/transcribe_vosk.py
```
Verás una terminal estilo "Matrix" transcribiendo en vivo.

---

## 📂 Estructura del Proyecto (Limpia)

```
Concejo_Analyzer/
├── model/                  # El cerebro de la IA (Vosk)
├── scripts/
│   ├── config.py           # Configuración (IDs, Rutas)
│   ├── docs_manager.py     # El Escriba (Conexión con Google)
│   ├── install_vosk_model.py # Utilidad de instalación
│   ├── list_audio.py       # Utilidad de diagnóstico de audio
│   └── transcribe_vosk.py  # EL ORQUESTADOR PRINCIPAL
├── credentials.json        # Llaves de acceso (¡NO SUBIR A GITHUB!)
├── requirements.txt        # Dependencias
└── README.md               # Este archivo
```

---

## 🤖 Créditos
Desarrollado como parte del entrenamiento en la Matrix.
**Arquitecto:** Sajor
**Consejero:** Morfeo (AI Agent)