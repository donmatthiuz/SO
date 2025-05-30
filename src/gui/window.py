# main.py
import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QSpinBox, QLabel, 
                             QMessageBox, QGroupBox, QGridLayout, QFrame)
# ===================================

# gui.py
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QComboBox, QSpinBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt

class SimuladorGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gantt_window = None  # Para mantener referencia a la ventana
        self.init_ui()
    
    def init_ui(self):
        # Widget central
        central = QWidget(self)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)  # Espacio entre elementos
        main_layout.setContentsMargins(20, 20, 20, 20)  # Márgenes
        
        # === SECCIÓN DE CONFIGURACIÓN ===
        config_group = QGroupBox("Configuración del Algoritmo")
        config_layout = QGridLayout(config_group)
        
        # Etiqueta y combo para algoritmo
        label_algoritmo = QLabel("Algoritmo de Planificación:")
        self.combo_algoritmo = QComboBox(self)
        self.combo_algoritmo.addItems([
            "First In First Out (FIFO)",
            "Shortest Job First (SJF)",
            "Shortest Remaining Time (SRT)",
            "Round Robin",
            "Priority Scheduling"
        ])
        
        # Etiqueta y spin para quantum (inicialmente ocultos)
        self.label_quantum = QLabel("Quantum:")
        self.spin_quantum = QSpinBox(self)
        self.spin_quantum.setRange(1, 50)
        self.spin_quantum.setValue(4)
        self.spin_quantum.setSuffix(" unidades")
        
        # Ocultar quantum al inicio
        self.label_quantum.setVisible(False)
        self.spin_quantum.setVisible(False)
        
        # Agregar a grid layout
        config_layout.addWidget(label_algoritmo, 0, 0)
        config_layout.addWidget(self.combo_algoritmo, 0, 1)
        config_layout.addWidget(self.label_quantum, 1, 0)
        config_layout.addWidget(self.spin_quantum, 1, 1)
        
        # === SECCIÓN DE SIMULACIONES ===
        sim_group = QGroupBox("Ejecutar Simulación")
        sim_layout = QHBoxLayout(sim_group)
        
        self.btn_sim_a = QPushButton("Simulación A\n(Planificación)", self)
        self.btn_sim_b = QPushButton("Simulación B\n(Sincronización)", self)
        
        # Estilo para botones
        button_style = """
            QPushButton {
                padding: 15px;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #007ACC;
                border-radius: 8px;
                background-color: #E6F3FF;
            }
            QPushButton:hover {
                background-color: #CCE7FF;
                border-color: #0056A3;
            }
            QPushButton:pressed {
                background-color: #B3DBFF;
            }
        """
        
        self.btn_sim_a.setStyleSheet(button_style)
        self.btn_sim_b.setStyleSheet(button_style)
        self.btn_sim_a.setMinimumHeight(60)
        self.btn_sim_b.setMinimumHeight(60)
        
        sim_layout.addWidget(self.btn_sim_a)
        sim_layout.addWidget(self.btn_sim_b)
        
        # === LÍNEA SEPARADORA ===
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        # === INFORMACIÓN ===
        info_label = QLabel("💡 Selecciona un algoritmo y presiona un botón para ejecutar la simulación")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 10px;
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 5px;
            }
        """)
        
        # === AGREGAR TODO AL LAYOUT PRINCIPAL ===
        main_layout.addWidget(config_group)
        main_layout.addWidget(sim_group)
        main_layout.addWidget(line)
        main_layout.addWidget(info_label)
        main_layout.addStretch()  # Empuja todo hacia arriba
        
        # === CONECTAR SEÑALES ===
        self.combo_algoritmo.currentTextChanged.connect(self.on_algoritmo_changed)
        self.btn_sim_a.clicked.connect(self.on_simulacion_a_clicked)
        self.btn_sim_b.clicked.connect(self.on_simulacion_b_clicked)
        
        # === CONFIGURAR VENTANA ===
        self.setCentralWidget(central)
        self.setWindowTitle("Simulador de Sistemas Operativos")
        self.setMinimumSize(500, 400)  # Tamaño mínimo
        self.resize(600, 450)  # Tamaño inicial
        
        # Centrar ventana en pantalla
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        screen = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        screen.moveCenter(center_point)
        self.move(screen.topLeft())
    
    def on_algoritmo_changed(self, text):
        """Muestra/oculta el campo quantum según el algoritmo seleccionado"""
        es_rr = "round robin" in text.lower()
        self.label_quantum.setVisible(es_rr)
        self.spin_quantum.setVisible(es_rr)
        
        # Ajustar tamaño de la ventana si es necesario
        if es_rr:
            self.setMinimumSize(500, 450)
        else:
            self.setMinimumSize(500, 400)
    
    def on_simulacion_a_clicked(self):
        """Maneja el clic en Simulación A (Planificación)"""
        try:
           
            procesos = cargar_procesos_desde_archivo("data/procesos.txt")
            if not procesos:
                QMessageBox.warning(self, "Error", "No se cargaron procesos.")
                return
            
            algoritmo = self.combo_algoritmo.currentText()
            quantum = self.spin_quantum.value()
            
            # Ejecutar algoritmo seleccionado
            if "fifo" in algoritmo.lower():
                resultado_simulacion = fifo(procesos)
            elif "round robin" in algoritmo.lower():
                resultado_simulacion = round_robin(procesos, quantum)
            else:
                QMessageBox.information(self, "Info", 
                    f"El algoritmo '{algoritmo}' aún no está implementado.\n"
                    "Algoritmos disponibles: FIFO y Round Robin")
                return
            
            # Cerrar ventana anterior si existe
            if self.gantt_window:
                self.gantt_window.close()
            
            # Mostrar nueva tabla de Gantt
            self.gantt_window = GanttTableWindow(resultado_simulacion, self)
            self.gantt_window.show()
            
            # Posicionar ventana Gantt al lado de la ventana principal
            self.position_gantt_window()
            
            # Mostrar estadísticas
            estadisticas = generar_estadisticas(resultado_simulacion)
            QMessageBox.information(self, "Estadísticas de la Simulación", estadisticas)
            
        except ImportError as e:
            QMessageBox.critical(self, "Error de Importación", 
                f"No se pudieron importar los módulos necesarios:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la simulación: {str(e)}")
    
    def position_gantt_window(self):
        """Posiciona la ventana Gantt al lado de la ventana principal"""
        if self.gantt_window:
            # Obtener posición y tamaño de la ventana principal
            main_pos = self.pos()
            main_size = self.size()
            
            # Posicionar Gantt a la derecha de la ventana principal
            gantt_x = main_pos.x() -100
            gantt_y = main_pos.y() +100
            
            self.gantt_window.move(gantt_x, gantt_y)
    
    def on_simulacion_b_clicked(self):
        """Maneja el clic en Simulación B (Sincronización)"""
        QMessageBox.information(self, "Simulación B", 
            "La Simulación B (Sincronización de Procesos) aún no está implementada.\n\n"
            "Esta simulación incluirá:\n"
            "• Mutex y Semáforos\n"
            "• Sincronización de procesos\n"
            "• Recursos compartidos")
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana principal"""
        if self.gantt_window:
            self.gantt_window.close()
        event.accept()

# proceso.py
class Proceso:
    def __init__(self, pid, tiempo_llegada, tiempo_cpu, prioridad=0):
        self.pid = pid
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_cpu = tiempo_cpu
        self.prioridad = prioridad
        self.tiempo_restante = tiempo_cpu
        self.tiempo_inicio = None
        self.tiempo_fin = None
        self.tiempo_espera = 0
        self.tiempo_respuesta = None
    
    def __str__(self):
        return f"Proceso({self.pid}, TA:{self.tiempo_llegada}, CPU:{self.tiempo_cpu})"

class ResultadoSimulacion:
    def __init__(self, procesos, tabla_ejecucion, tiempo_total):
        self.procesos = procesos  # Lista de procesos originales
        self.tabla_ejecucion = tabla_ejecucion  # Diccionario con la ejecución por tiempo
        self.tiempo_total = tiempo_total
        
    def get_proceso_en_tiempo(self, tiempo):
        """Retorna el proceso que se ejecuta en un tiempo dado"""
        return self.tabla_ejecucion.get(tiempo, None)

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
            Proceso("A", 0, 3, 1),
            Proceso("B", 2, 6, 2),
            Proceso("C", 4, 4, 3),
             Proceso("D", 8, 2, 4),
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
    tabla_ejecucion = {}
    
    for proceso in procesos_copia:
        # Si el proceso llega después del tiempo actual, avanzar tiempo
        if tiempo_actual < proceso.tiempo_llegada:
            tiempo_actual = proceso.tiempo_llegada
        
        # Marcar tiempo de inicio si es la primera vez
        if proceso.tiempo_inicio is None:
            proceso.tiempo_inicio = tiempo_actual
            proceso.tiempo_respuesta = tiempo_actual - proceso.tiempo_llegada
        
        # Ejecutar el proceso
        for i in range(proceso.tiempo_cpu):
            estado = "EJECUTANDO"
            if i == proceso.tiempo_cpu - 1:  # Último ciclo
                estado = "TERMINADO"
                proceso.tiempo_fin = tiempo_actual + 1
            
            tabla_ejecucion[tiempo_actual] = {
                'proceso': proceso,
                'estado': estado,
                'tiempo_restante': proceso.tiempo_cpu - i - 1
            }
            tiempo_actual += 1
        
        # Calcular tiempo de espera
        proceso.tiempo_espera = proceso.tiempo_inicio - proceso.tiempo_llegada
    
    return ResultadoSimulacion(procesos_copia, tabla_ejecucion, tiempo_actual)

def round_robin(procesos, quantum):
    """Algoritmo Round Robin"""
    procesos_copia = copy.deepcopy(procesos)
    procesos_copia.sort(key=lambda p: p.tiempo_llegada)
    
    cola = []
    tabla_ejecucion = {}
    tiempo_actual = 0
    i = 0
    
    # Agregar procesos que llegan en tiempo 0
    while i < len(procesos_copia) and procesos_copia[i].tiempo_llegada <= tiempo_actual:
        cola.append(procesos_copia[i])
        i += 1
    
    while cola or i < len(procesos_copia):
        # Si no hay procesos en cola, avanzar al siguiente proceso
        if not cola:
            if i < len(procesos_copia):
                tiempo_actual = procesos_copia[i].tiempo_llegada
                cola.append(procesos_copia[i])
                i += 1
            continue
        
        proceso_actual = cola.pop(0)
        
        # Marcar tiempo de inicio si es la primera vez
        if proceso_actual.tiempo_inicio is None:
            proceso_actual.tiempo_inicio = tiempo_actual
            proceso_actual.tiempo_respuesta = tiempo_actual - proceso_actual.tiempo_llegada
        
        # Ejecutar por quantum o hasta terminar
        tiempo_ejecucion = min(quantum, proceso_actual.tiempo_restante)
        
        for j in range(tiempo_ejecucion):
            estado = "EJECUTANDO"
            proceso_actual.tiempo_restante -= 1
            
            if proceso_actual.tiempo_restante == 0:  # Proceso termina
                estado = "TERMINADO"
                proceso_actual.tiempo_fin = tiempo_actual + 1
            
            tabla_ejecucion[tiempo_actual] = {
                'proceso': proceso_actual,
                'estado': estado,
                'tiempo_restante': proceso_actual.tiempo_restante
            }
            tiempo_actual += 1
        
        # Agregar procesos que llegaron durante la ejecución
        while i < len(procesos_copia) and procesos_copia[i].tiempo_llegada <= tiempo_actual:
            cola.append(procesos_copia[i])
            i += 1
        
        # Si el proceso no terminó, agregarlo de nuevo a la cola
        if proceso_actual.tiempo_restante > 0:
            cola.append(proceso_actual)
    
    # Calcular tiempos de espera
    for proceso in procesos_copia:
        if proceso.tiempo_inicio is not None and proceso.tiempo_fin is not None:
            tiempo_total = proceso.tiempo_fin - proceso.tiempo_llegada
            proceso.tiempo_espera = tiempo_total - proceso.tiempo_cpu
    
    return ResultadoSimulacion(procesos_copia, tabla_ejecucion, tiempo_actual)

def generar_estadisticas(resultado):
    """Genera estadísticas de la simulación"""
    procesos = resultado.procesos
    tiempo_total = resultado.tiempo_total
    
    if not procesos:
        return "No hay procesos para mostrar estadísticas."
    
    # Calcular promedios
    tiempo_espera_total = sum(p.tiempo_espera for p in procesos if p.tiempo_espera is not None)
    tiempo_respuesta_total = sum(p.tiempo_respuesta for p in procesos if p.tiempo_respuesta is not None)
    
    promedio_espera = tiempo_espera_total / len(procesos)
    promedio_respuesta = tiempo_respuesta_total / len(procesos)
    
    estadisticas = f"=== ESTADÍSTICAS ===\n"
    estadisticas += f"Tiempo total de simulación: {tiempo_total}\n"
    estadisticas += f"Tiempo de espera promedio: {promedio_espera:.2f}\n"
    estadisticas += f"Tiempo de respuesta promedio: {promedio_respuesta:.2f}\n\n"
    
    estadisticas += "=== DETALLES POR PROCESO ===\n"
    for proceso in procesos:
        estadisticas += f"{proceso.pid}: "
        estadisticas += f"Llegada={proceso.tiempo_llegada}, "
        estadisticas += f"CPU={proceso.tiempo_cpu}, "
        estadisticas += f"Inicio={proceso.tiempo_inicio}, "
        estadisticas += f"Fin={proceso.tiempo_fin}, "
        estadisticas += f"Espera={proceso.tiempo_espera}, "
        estadisticas += f"Respuesta={proceso.tiempo_respuesta}\n"
    
    return estadisticas

# ===================================

# gantt_table_window.py
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QPushButton, QHBoxLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QBrush

class GanttTableWindow(QWidget):
    def __init__(self, resultado_simulacion, parent=None):
        super().__init__(parent)
        self.resultado = resultado_simulacion
        self.tiempo_actual = 0
        self.colores = {}
        self.init_ui()
        self.asignar_colores()
        self.setup_table()
        self.init_timer()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Etiqueta de título
        self.label_titulo = QLabel("Diagrama de Gantt - Tabla de Ejecución", self)
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        
        # Etiqueta de tiempo actual
        self.label_tiempo = QLabel(f"Tiempo actual: {self.tiempo_actual}", self)
        self.label_tiempo.setAlignment(Qt.AlignCenter)
        self.label_tiempo.setStyleSheet("font-size: 14px; margin: 5px;")
        
        # Tabla principal
        self.tabla = QTableWidget(self)
        
        # Controles
        controles_layout = QHBoxLayout()
        self.btn_pausar = QPushButton("Pausar", self)
        self.btn_reanudar = QPushButton("Reanudar", self)
        self.btn_reiniciar = QPushButton("Reiniciar", self)
        
        controles_layout.addWidget(self.btn_pausar)
        controles_layout.addWidget(self.btn_reanudar)
        controles_layout.addWidget(self.btn_reiniciar)
        
        # Agregar widgets al layout
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_tiempo)
        layout.addWidget(self.tabla)
        layout.addLayout(controles_layout)
        
        # Conectar botones
        self.btn_pausar.clicked.connect(self.pausar_animacion)
        self.btn_reanudar.clicked.connect(self.reanudar_animacion)
        self.btn_reiniciar.clicked.connect(self.reiniciar_animacion)
        
        self.setLayout(layout)
        self.setWindowTitle("Tabla de Gantt")
        self.resize(800, 400)
    
    def asignar_colores(self):
        """Asigna un color único a cada proceso"""
        for proceso in self.resultado.procesos:
            if proceso.pid not in self.colores:
                # Generar color aleatorio
                hue = random.randint(0, 359)
                color = QColor.fromHsv(hue, 180, 220)
                self.colores[proceso.pid] = color
    
    def setup_table(self):
        """Configura la tabla inicial"""
        # Configurar filas (procesos)
        procesos = self.resultado.procesos
        self.tabla.setRowCount(len(procesos))
        
        # Configurar columnas (tiempo)
        tiempo_total = self.resultado.tiempo_total
        self.tabla.setColumnCount(tiempo_total)
        
        # Headers de filas (PIDs)
        row_headers = [proceso.pid for proceso in procesos]
        self.tabla.setVerticalHeaderLabels(row_headers)
        
        # Headers de columnas (tiempo)
        col_headers = [str(t) for t in range(tiempo_total)]
        self.tabla.setHorizontalHeaderLabels(col_headers)
        
        # Ajustar tamaños
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        for i in range(tiempo_total):
            self.tabla.setColumnWidth(i, 60)
        
        # Inicializar celdas vacías
        for fila in range(len(procesos)):
            for columna in range(tiempo_total):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, columna, item)
    
    def init_timer(self):
        """Inicializa el timer para la animación"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tabla)
        self.timer.start(800)  # Actualiza cada 800ms
    
    def actualizar_tabla(self):
        """Actualiza la tabla con el siguiente paso de tiempo"""
        if self.tiempo_actual >= self.resultado.tiempo_total:
            self.timer.stop()
            self.label_tiempo.setText(f"Simulación completada - Tiempo total: {self.resultado.tiempo_total}")
            return
        
        # Actualizar etiqueta de tiempo
        self.label_tiempo.setText(f"Tiempo actual: {self.tiempo_actual}")
        
        # Obtener información del tiempo actual
        info_tiempo = self.resultado.tabla_ejecucion.get(self.tiempo_actual)
        
        if info_tiempo:
            proceso = info_tiempo['proceso']
            estado = info_tiempo['estado']
            tiempo_restante = info_tiempo['tiempo_restante']
            
            # Encontrar la fila del proceso
            fila = -1
            for i, p in enumerate(self.resultado.procesos):
                if p.pid == proceso.pid:
                    fila = i
                    break
            
            if fila >= 0:
                # Crear texto para la celda
                if estado == "TERMINADO":
                    texto = "FIN"
                else:
                    texto = f"RUN\n({tiempo_restante})"
                
                # Actualizar celda
                item = self.tabla.item(fila, self.tiempo_actual)
                item.setText(texto)
                
                # Aplicar color
                color = self.colores[proceso.pid]
                item.setBackground(QBrush(color))
                
                # Estilo especial para proceso terminado
                if estado == "TERMINADO":
                    item.setBackground(QBrush(QColor(255, 100, 100)))  # Rojo para terminado
        
        self.tiempo_actual += 1
    
    def pausar_animacion(self):
        """Pausa la animación"""
        self.timer.stop()
    
    def reanudar_animacion(self):
        """Reanuda la animación"""
        if self.tiempo_actual < self.resultado.tiempo_total:
            self.timer.start(800)
    
    def reiniciar_animacion(self):
        """Reinicia la animación"""
        self.timer.stop()
        self.tiempo_actual = 0
        self.setup_table()
        self.timer.start(800)

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