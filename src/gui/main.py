# main.py
import sys
from PyQt5.QtWidgets import QApplication


# ===================================

# gui.py
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QComboBox, QSpinBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt

class SimuladorGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        # Widget central
        central = QWidget(self)
        layout = QVBoxLayout(central)
        
        # Crear widgets
        self.combo_algoritmo = QComboBox(self)
        self.combo_algoritmo.addItems([
            "First In First Out (FIFO)",
            "Shortest Job First (SJF)",
            "Shortest Remaining Time (SRT)",
            "Round Robin",
            "Priority Scheduling"
        ])
        
        self.label_quantum = QLabel("Quantum:", self)
        self.spin_quantum = QSpinBox(self)
        self.spin_quantum.setRange(1, 50)
        self.spin_quantum.setValue(4)
        
        self.btn_sim_a = QPushButton("Simulación A", self)
        self.btn_sim_b = QPushButton("Simulación B", self)
        
        # Agregar widgets al layout
        layout.addWidget(self.combo_algoritmo)
        layout.addWidget(self.label_quantum)
        layout.addWidget(self.spin_quantum)
        layout.addWidget(self.btn_sim_a)
        layout.addWidget(self.btn_sim_b)
        
        # Ocultar quantum al inicio
        self.label_quantum.setVisible(False)
        self.spin_quantum.setVisible(False)
        
        # Conectar señales
        self.combo_algoritmo.currentTextChanged.connect(self.on_algoritmo_changed)
        self.btn_sim_a.clicked.connect(self.on_simulacion_a_clicked)
        self.btn_sim_b.clicked.connect(self.on_simulacion_b_clicked)
        
        self.setCentralWidget(central)
        self.setWindowTitle("Simulador de Sistemas Operativos")
        self.resize(300, 200)
    
    def on_algoritmo_changed(self, text):
        es_rr = "round robin" in text.lower()
        self.label_quantum.setVisible(es_rr)
        self.spin_quantum.setVisible(es_rr)
    
    def on_simulacion_a_clicked(self):
        try:
            procesos = cargar_procesos_desde_archivo("data/procesos.txt")
            if not procesos:
                QMessageBox.warning(self, "Error", "No se cargaron procesos.")
                return
            
            algoritmo = self.combo_algoritmo.currentText()
            quantum = self.spin_quantum.value()
            
            if "fifo" in algoritmo.lower():
                ejecutados = fifo(procesos)
            elif "round robin" in algoritmo.lower():
                ejecutados = round_robin(procesos, quantum)
            else:
                QMessageBox.information(self, "Info", "Ese algoritmo aún no está implementado.")
                return
            
            resultado = "Orden de ejecución:\n"
            for p in ejecutados:
                resultado += f"{p.pid}\n"
            
            # Calcular tiempo de espera promedio
            promedio = calcular_tiempo_espera_promedio(procesos, ejecutados)
            resultado += f"\nTiempo de espera promedio: {promedio:.2f}"
            
            # Mostrar diagrama de Gantt
            self.gantt_window = GanttWindow(ejecutados, self)
            self.gantt_window.show()
            
            QMessageBox.information(self, "Resultado", resultado)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la simulación: {str(e)}")
    
    def on_simulacion_b_clicked(self):
        QMessageBox.information(self, "Info", "Simulación B aún no implementada.")

# ===================================

# proceso.py
class Proceso:
    def __init__(self, pid, tiempo_llegada, tiempo_cpu, prioridad=0):
        self.pid = pid
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_cpu = tiempo_cpu
        self.prioridad = prioridad
        self.tiempo_restante = tiempo_cpu
        self.tiempo_inicio = 0
        self.tiempo_fin = 0
        self.tiempo_espera = 0
    
    def __str__(self):
        return f"Proceso({self.pid}, TA:{self.tiempo_llegada}, CPU:{self.tiempo_cpu})"

def cargar_procesos_desde_archivo(archivo):
    """Carga procesos desde un archivo de texto"""
    procesos = []
    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith('#'):
                    partes = linea.split()
                    if len(partes) >= 3:
                        pid = partes[0]
                        tiempo_llegada = int(partes[1])
                        tiempo_cpu = int(partes[2])
                        prioridad = int(partes[3]) if len(partes) > 3 else 0
                        procesos.append(Proceso(pid, tiempo_llegada, tiempo_cpu, prioridad))
    except FileNotFoundError:
        # Si no existe el archivo, crear procesos de ejemplo
        procesos = [
            Proceso("P1", 0, 8, 3),
            Proceso("P2", 1, 4, 1),
            Proceso("P3", 2, 9, 4),
            Proceso("P4", 3, 5, 2),
            Proceso("P5", 4, 2, 5)
        ]
    except Exception as e:
        print(f"Error cargando procesos: {e}")
    
    return procesos

# ===================================

# algoritmo.py
import copy

def fifo(procesos):
    """Algoritmo First In First Out (FIFO)"""
    procesos_copia = copy.deepcopy(procesos)
    procesos_copia.sort(key=lambda p: p.tiempo_llegada)
    
    tiempo_actual = 0
    ejecutados = []
    
    for proceso in procesos_copia:
        if tiempo_actual < proceso.tiempo_llegada:
            tiempo_actual = proceso.tiempo_llegada
        
        proceso.tiempo_inicio = tiempo_actual
        proceso.tiempo_fin = tiempo_actual + proceso.tiempo_cpu
        proceso.tiempo_espera = proceso.tiempo_inicio - proceso.tiempo_llegada
        tiempo_actual = proceso.tiempo_fin
        
        # Agregar bloques de ejecución
        for _ in range(proceso.tiempo_cpu):
            ejecutados.append(copy.copy(proceso))
    
    return ejecutados

def round_robin(procesos, quantum):
    """Algoritmo Round Robin"""
    procesos_copia = copy.deepcopy(procesos)
    cola = []
    ejecutados = []
    tiempo_actual = 0
    i = 0
    
    # Ordenar por tiempo de llegada
    procesos_copia.sort(key=lambda p: p.tiempo_llegada)
    
    # Agregar el primer proceso que llegue
    if procesos_copia:
        cola.append(procesos_copia[0])
        i = 1
    
    while cola or i < len(procesos_copia):
        if not cola:
            # Si no hay procesos en cola, avanzar al siguiente
            if i < len(procesos_copia):
                tiempo_actual = procesos_copia[i].tiempo_llegada
                cola.append(procesos_copia[i])
                i += 1
            continue
        
        proceso_actual = cola.pop(0)
        
        # Ejecutar por quantum o hasta terminar
        tiempo_ejecucion = min(quantum, proceso_actual.tiempo_restante)
        
        for _ in range(tiempo_ejecucion):
            ejecutados.append(copy.copy(proceso_actual))
        
        tiempo_actual += tiempo_ejecucion
        proceso_actual.tiempo_restante -= tiempo_ejecucion
        
        # Agregar procesos que llegaron durante la ejecución
        while i < len(procesos_copia) and procesos_copia[i].tiempo_llegada <= tiempo_actual:
            cola.append(procesos_copia[i])
            i += 1
        
        # Si el proceso no terminó, agregarlo de nuevo a la cola
        if proceso_actual.tiempo_restante > 0:
            cola.append(proceso_actual)
    
    return ejecutados

def calcular_tiempo_espera_promedio(procesos_originales, ejecucion):
    """Calcula el tiempo de espera promedio"""
    if not procesos_originales:
        return 0.0
    
    # Calcular tiempo de espera para cada proceso
    tiempos_espera = {}
    tiempos_inicio = {}
    
    # Encontrar el primer tiempo de inicio de cada proceso
    for i, bloque in enumerate(ejecucion):
        if bloque.pid not in tiempos_inicio:
            tiempos_inicio[bloque.pid] = i
    
    # Calcular tiempo de espera
    for proceso in procesos_originales:
        if proceso.pid in tiempos_inicio:
            tiempo_espera = tiempos_inicio[proceso.pid] - proceso.tiempo_llegada
            tiempos_espera[proceso.pid] = max(0, tiempo_espera)
        else:
            tiempos_espera[proceso.pid] = 0
    
    promedio = sum(tiempos_espera.values()) / len(tiempos_espera)
    return promedio

# ===================================

# gantt_window.py
import random
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor

class GanttWindow(QWidget):
    def __init__(self, ejecucion, parent=None):
        super().__init__(parent)
        self.ejecucion = ejecucion
        self.indice = 0
        self.colores = {}
        self.init_ui()
        self.asignar_colores()
        self.init_timer()
    
    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(2)
        self.setLayout(self.layout)
        self.setWindowTitle("Diagrama de Gantt")
        self.resize(800, 100)
    
    def asignar_colores(self):
        """Asigna un color único a cada proceso"""
        for proceso in self.ejecucion:
            if proceso.pid not in self.colores:
                # Generar color aleatorio
                hue = random.randint(0, 359)
                color = QColor.fromHsv(hue, 255, 200)
                self.colores[proceso.pid] = color
    
    def init_timer(self):
        """Inicializa el timer para la animación"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mostrar_siguiente_bloque)
        self.timer.start(500)  # muestra un bloque cada 500ms
    
    def mostrar_siguiente_bloque(self):
        """Muestra el siguiente bloque en el diagrama de Gantt"""
        if self.indice >= len(self.ejecucion):
            self.timer.stop()
            return
        
        proceso = self.ejecucion[self.indice]
        self.indice += 1
        
        bloque = QLabel(proceso.pid, self)
        bloque.setAlignment(Qt.AlignCenter)
        bloque.setFixedSize(40, 40)
        bloque.setFrameShape(QFrame.Box)
        
        color = self.colores[proceso.pid]
        bloque.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
        
        self.layout.addWidget(bloque)

# ===================================

# Crear archivo data/procesos.txt (opcional)
"""
# Formato: PID tiempo_llegada tiempo_cpu prioridad
P1 0 8 3
P2 1 4 1
P3 2 9 4
P4 3 5 2
P5 4 2 5
"""

def main():
    app = QApplication(sys.argv)
    ventana = SimuladorGUI()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
