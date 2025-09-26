from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from serial.tools import list_ports

class PortMonitor(QObject):
    ports_changed = pyqtSignal(list)   # emite lista de strings con los nombres (device)

    def __init__(self, interval_ms: int = 1000, parent=None):
        super().__init__(parent)
        self._timer = QTimer()
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._scan)
        self._known = set()

    def start(self):
        self._scan()  # primer escaneo inmediato
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def _scan(self):
        current = {p.device for p in list_ports.comports()} # CONJUNTOS SET 
        if current != self._known:
            self._known = current
            self.ports_changed.emit(sorted(current))
