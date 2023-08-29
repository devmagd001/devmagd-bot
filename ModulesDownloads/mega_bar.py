import sys
import time
import threading

class ProgressMonitor:
    def __init__(self, total_size):
        self.total_size = total_size
        self.current_size = 0
        self.lock = threading.Lock()
        
        # Inicia un hilo para actualizar el progreso
        self.thread = threading.Thread(target=self.update_progress)
        self.thread.daemon = True
        self.thread.start()

    def update_progress(self):
        while True:
            # Calcula el porcentaje de progreso
            progress = (self.current_size / self.total_size) * 100

            # Muestra el progreso actual
            sys.stdout.write(f"\rProgreso: {progress:.2f}%")
            sys.stdout.flush()

            # Espera 1 segundo antes de actualizar el progreso de nuevo
            time.sleep(1)

    def update_size(self, size):
        with self.lock:
            self.current_size += size

# Sobrescribe la función download_url de la clase Mega para agregar la opción de mostrar el progreso
def download_url_with_progress(self, url, dest_filename=None, progress_callback=None, **kwargs):
    response = self.http_client.get(url, stream=True, **kwargs)
    total_size = int(response.headers.get('Content-Length', 0))
    progress_monitor = ProgressMonitor(total_size)

    with open(dest_filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            progress_monitor.update_size(len(chunk))

    sys.stdout.write('\n')
    sys.stdout.flush()