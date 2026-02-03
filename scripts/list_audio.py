import pyaudio

def list_devices():
    p = pyaudio.PyAudio()
    print("\n--- LISTA DE DISPOSITIVOS DE AUDIO ---")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"ID: {i} | Nombre: {info['name']} | Canales: {info['maxInputChannels']}")
    p.terminate()

if __name__ == "__main__":
    list_devices()
