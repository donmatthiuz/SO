import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QSpinBox, QLabel, 
                             QMessageBox, QGroupBox, QGridLayout, QFrame)
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QComboBox, QSpinBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from src.structure.process import cargar_procesos_desde_archivo
from src.gui.table_schedule import GanttTableWindow
from src.scheduling.resultados import generar_estadisticas
from src.scheduling.FIFO import FIFO
from src.scheduling.Round_Robin import RoundRobin
from src.scheduling.FIFO import FIFO
from src.scheduling.Round_Robin import RoundRobin

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
        
      
        config_group = QGroupBox("Configuración del Algoritmo")
        config_layout = QGridLayout(config_group)
        
       
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
           
            procesos = cargar_procesos_desde_archivo("data/procesors.txt")
            if not procesos:
                QMessageBox.warning(self, "Error", "No se cargaron procesos.")
                return
            
            algoritmo = self.combo_algoritmo.currentText()
            quantum = self.spin_quantum.value()
            

            # Ejecutar algoritmo seleccionado
            if "fifo" in algoritmo.lower():

                scheduler = FIFO(procesos=procesos)
                resultado_simulacion = scheduler.simular()
            elif "round robin" in algoritmo.lower():
                scheduler = RoundRobin(quantum=4, procesos=procesos)
                resultado_simulacion = scheduler.simular()
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
            gantt_x = main_pos.x() +40
            gantt_y = main_pos.y() +270
            
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
