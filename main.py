import sys
from PyQt6.QtCore import Qt, QThread, pyqtSlot, QDateTime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
    QPushButton, QPlainTextEdit, QLabel
)
from port_monitor import PortMonitor
from serial_reader import SerialReader

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Escáner Serial + Consola (Hot-Plug)")

        # --- Widgets UI ---
        self.port_label = QLabel("Puerto:")
        self.port_combo = QComboBox()
        self.baud_label = QLabel("Baudios:")
        self.baud_input = QLineEdit("115200")
        self.baud_input.setFixedWidth(100)
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.setCheckable(True)

        top_row = QHBoxLayout()
        top_row.addWidget(self.port_label)
        top_row.addWidget(self.port_combo, 1)
        top_row.addWidget(self.baud_label)
        top_row.addWidget(self.baud_input)
        top_row.addWidget(self.connect_btn)

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Datos recibidos aparecerán aquí...")

        layout = QVBoxLayout(self)
        layout.addLayout(top_row)
        layout.addWidget(self.console, 1)

        # --- Hilo PortMonitor ---
        self.monitor_thread = QThread(self)
        self.monitor = PortMonitor(interval_ms=1000)      # escaneo 1s
        self.monitor.ports_changed.connect(self.on_ports_changed)
        self.monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.monitor.start)
        self.monitor_thread.start()

        # --- Lector Serial (en su propio hilo pero con internals thread) ---
        self.reader = SerialReader()
        self.reader.data_received.connect(self.on_data_received)
        self.reader.port_opened.connect(self.on_port_opened)
        self.reader.port_closed.connect(self.on_port_closed)
        self.reader.port_error.connect(self.on_port_error)

        # --- Señales UI ---
        self.connect_btn.toggled.connect(self.on_connect_toggled)

        # Estado
        self._last_ports = []
 
    # ---------- Slots de PortMonitor ---------- 
    #CADA VEZ QUE EL POR MONITOR DETECTA NUEVOS PUERTOS O CAMBIO EN LISTA DE PUERTOS
    @pyqtSlot(list)
    def on_ports_changed(self, ports: list):
        now = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
        # Actualizar la UI (desde el hilo principal)
        self._last_ports = ports
        current = self.port_combo.currentText()
        self.port_combo.blockSignals(True)
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        self.port_combo.blockSignals(False)

        self._append_log(f"[{now}] Puertos detectados: {ports if ports else '— ninguno —'}")

        # Si estábamos conectados y el puerto desaparece, desconectar
        if self.connect_btn.isChecked() and current and current not in ports:
            self._append_log(f"[{now}] Puerto '{current}' ya no está disponible. Desconectando...")
            self.connect_btn.setChecked(False)  # esto llama a on_connect_toggled(False)

    # ---------- Slots de SerialReader ---------- 
    #CUANDO EL SERIA RECIBE DATOS NUEVOS
    @pyqtSlot(bytes)
    def on_data_received(self, data: bytes):
        # Decodifica de manera robusta (UTF-8 con reemplazo)
        try:
            text = data.decode('utf-8', errors='replace')
        except Exception:
            text = repr(data)
        # Agregar sin bloquear
        self.console.appendPlainText(text.rstrip("\n"))

    @pyqtSlot(str)
    def on_port_opened(self, name: str):
        self._append_log(f"✔ Conectado a {name}")

    @pyqtSlot(str)
    def on_port_closed(self, name: str):
        self._append_log(f"✖ Desconectado de {name}")

    @pyqtSlot(str)
    def on_port_error(self, msg: str):
        self._append_log(f"⚠ Error: {msg}")
        # Si falló la conexión, revertir botón
        if self.connect_btn.isChecked():
            self.connect_btn.setChecked(False)

    # ---------- Interacción UI ---------- 
    # ESTE METODO ES LLAMADO CUANDO LE DA COECTAR O DESCONECTAR
    @pyqtSlot(bool)
    def on_connect_toggled(self, checked: bool):
        if checked:
            port = self.port_combo.currentText().strip()
            if not port:
                self._append_log("⚠ No hay puerto seleccionado.")
                self.connect_btn.setChecked(False)
                return
            try:
                baud = int(self.baud_input.text())
            except ValueError:
                self._append_log("⚠ Baudios inválidos.")
                self.connect_btn.setChecked(False)
                return
            self._append_log(f"Intentando conectar a {port} @ {baud}...")
            self.reader.open(port, baud)
            self.connect_btn.setText("Desconectar")
            self.port_combo.setEnabled(False)
            self.baud_input.setEnabled(False)
        else:
            self.reader.close()
            self.connect_btn.setText("Conectar")
            self.port_combo.setEnabled(True)
            self.baud_input.setEnabled(True)

    def _append_log(self, line: str):
        self.console.appendPlainText(line)

    def closeEvent(self, event): #METODO LLAMADO CUANDO USUARIO CIERRA LA VENTANA
        try:
            self.reader.close()
        except Exception:
            pass
        try:
            self.monitor.stop()
            self.monitor_thread.quit()
            self.monitor_thread.wait(1000)
        except Exception:
            pass
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(900, 500)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
