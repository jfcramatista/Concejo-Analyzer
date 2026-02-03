import os
import requests
import zipfile
from tqdm import tqdm

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
MODEL_ZIP = "vosk-model-small-es-0.42.zip"
MODEL_DIR = "model"

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    print(f"⬇️ Descargando modelo: {filename} ({total_size/1024/1024:.1f} MB)")
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def main():
    if os.path.exists(MODEL_DIR):
        print("✅ El modelo ya existe.")
        return

    try:
        download_file(MODEL_URL, MODEL_ZIP)
        
        print("📦 Descomprimiendo...")
        with zipfile.ZipFile(MODEL_ZIP, 'r') as zip_ref:
            zip_ref.extractall(".")
            
        # Renombrar carpeta extraida a 'model'
        os.rename("vosk-model-small-es-0.42", MODEL_DIR)
        
        # Limpiar zip
        os.remove(MODEL_ZIP)
        print("✨ ¡Modelo instalado correctamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
