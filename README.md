# 🔍 Escaner De Puertos Seriales

Una aplicación de monitoreo serial en tiempo real diseñada para laboratorios donde se conectan/desconectan frecuentemente microcontroladores (Arduino, ESP32), conversores USB-Serial y equipos industriales.

## 🚀 Características
- 🔍 **Detección Automática:** Scanner periódico de puertos cada 1 segundo
- ⚡ **Hot-Plug:** Detecta conexión/desconexión de dispositivos en tiempo real
- 📊 **Consola en Vivo:** Muestra tráfico de datos sin bloquear la interfaz gráfica
- 🔧 **Conexión Dinámica:** Selección de puerto y configuración de baudios en caliente
- 🛡️ **Thread-Safe:** Arquitectura multi-hilo segura para la GUI
  
## 🎯 Componentes Principales

- **Port Monitor (port_monitor.py):** Servicio de scanner periódico desacoplado
- **Serial Reader (serial_reader.py):** Componente separado para lectura de datos
- **GUI Main (main.py):** Interfaz gráfica principal con consola en vivo


## 🔧 Desarrollo Técnico
**Patrones Implementados**

- **Separación de concerns:** Lógica de negocio separada de la GUI
- **Comunicación thread-safe:** Mecanismos seguros entre hilos
- **Scanner no-bloqueante:** Detección de puertos sin afectar rendimiento

## 👨🏽‍💻 Autor
- [Daniel Mancia](https://github.com/Daniel-Mancia22) - DevMadCode
  
