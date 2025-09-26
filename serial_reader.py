# serial_reader.py
import threading
import time
import serial
from PyQt6.QtCore import QObject, pyqtSignal

class SerialReader(QObject):
    data_received = pyqtSignal(bytes)      # emite datos crudos
    port_opened   = pyqtSignal(str)        # abre nombre del puerto
    port_closed   = pyqtSignal(str)        # cierra nombre del puerto
    port_error    = pyqtSignal(str)        # mesnaje de error  mensaje de error

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ser = None
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._port_name = None

    def open(self, port_name: str, baudrate: int = 115200, timeout: float = 0.1): #puerto para abrir lectura
        """Abre el puerto y arranca el hilo de lectura."""
        self.close()  # por si había algo abierto
        try:
            self._ser = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
            self._port_name = port_name
        except Exception as e:
            self._ser = None
            self.port_error.emit(f"No se pudo abrir {port_name}: {e}")
            return

        self._stop.clear()
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        self.port_opened.emit(port_name)

    def close(self): # cerrar puerto
        """Cierra el puerto y detiene el hilo."""
        with self._lock:
            if self._ser is None:
                return
            port_name = self._port_name or "desconocido"
            self._stop.set()
            try:
                self._ser.close()
            except Exception:
                pass
            self._ser = None
            self._port_name = None
            self.port_closed.emit(port_name)

    def _read_loop(self):
        # Bucle de lectura no bloqueante
        while not self._stop.is_set():
            try:
                with self._lock:
                    ser = self._ser
                if ser is None:
                    break

                # read up to available bytes; timeout limita el bloqueo
                data = ser.read(1024)
                if data:
                    self.data_received.emit(data)
                else:
                    # pequeño sleep para no quemar CPU
                    time.sleep(0.01)
            except serial.SerialException as e:
                self.port_error.emit(f"Error de puerto: {e}")
                break
            except Exception as e:
                self.port_error.emit(f"Error de lectura: {e}")
                break

        # cierre defensivo si salimos del bucle
        with self._lock:
            if self._ser:
                try:
                    self._ser.close()
                except Exception:
                    pass
                finally:
                    name = self._port_name or "desconocido"
                    self._ser = None
                    self._port_name = None
                    self.port_closed.emit(name)
