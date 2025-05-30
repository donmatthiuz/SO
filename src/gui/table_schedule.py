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
