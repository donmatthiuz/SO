from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QPushButton, QHBoxLayout, QTextEdit)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QBrush


class SyncTableWindow(QWidget):
    def __init__(self, resultado_sincronizacion, parent=None):
        super().__init__(parent)
        self.resultado = resultado_sincronizacion
        self.ciclo_actual = 0
        self.colores_estado = {
            "ACCESED": QColor(100, 200, 100),      # Verde claro
            "RUNNING": QColor(100, 150, 255),    # Azul
            "BLOCKED": QColor(255, 150, 100),    # Naranja
            "FINISHED": QColor(200, 200, 200),   # Gris
            "WAITING": QColor(255, 255, 150)     # Amarillo
        }
        self.init_ui()
        self.setup_table()
        self.init_timer()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Etiqueta de título
        self.label_titulo = QLabel("Simulación de Sincronización", self)
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        
        # Etiqueta de ciclo actual
        self.label_ciclo = QLabel(f"Ciclo actual: {self.ciclo_actual}", self)
        self.label_ciclo.setAlignment(Qt.AlignCenter)
        self.label_ciclo.setStyleSheet("font-size: 14px; margin: 5px;")
        
        # Información de recursos
        self.label_recursos = QLabel("", self)
        self.label_recursos.setAlignment(Qt.AlignCenter)
        self.label_recursos.setStyleSheet("font-size: 12px; margin: 5px;")
        
        # Layout horizontal para tabla y detalle
        contenido_layout = QHBoxLayout()
        
        # Tabla principal
        self.tabla = QTableWidget(self)
        
        # Área de información detallada
        self.texto_detalle = QTextEdit(self)
        self.texto_detalle.setMinimumWidth(300)  # Ancho mínimo para el detalle
        self.texto_detalle.setMaximumWidth(400)  # Ancho máximo para el detalle
        self.texto_detalle.setMaximumHeight(100)  # Altura máxima reducida
        self.texto_detalle.setReadOnly(True)
        
        # Agregar tabla y detalle al layout horizontal
        contenido_layout.addWidget(self.tabla, 2)  # La tabla toma más espacio (proporción 2)
        contenido_layout.addWidget(self.texto_detalle, 1)  # El detalle toma menos espacio (proporción 1)
        
        # Controles
        controles_layout = QHBoxLayout()
        self.btn_pausar = QPushButton("Pausar", self)
        self.btn_reanudar = QPushButton("Reanudar", self)
        self.btn_reiniciar = QPushButton("Reiniciar", self)
        self.btn_siguiente = QPushButton("Siguiente Ciclo", self)
        
        controles_layout.addWidget(self.btn_pausar)
        controles_layout.addWidget(self.btn_reanudar)
        controles_layout.addWidget(self.btn_siguiente)
        controles_layout.addWidget(self.btn_reiniciar)
        
        # Agregar widgets al layout principal
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_ciclo)
        layout.addWidget(self.label_recursos)
        layout.addLayout(contenido_layout)  # Agregar el layout horizontal
        layout.addLayout(controles_layout)
        
        # Conectar botones
        self.btn_pausar.clicked.connect(self.pausar_animacion)
        self.btn_reanudar.clicked.connect(self.reanudar_animacion)
        self.btn_reiniciar.clicked.connect(self.reiniciar_animacion)
        self.btn_siguiente.clicked.connect(self.siguiente_ciclo)
        
        self.setLayout(layout)
        self.setWindowTitle("Tabla de Sincronización")
        self.resize(1200, 400)  # Reducido la altura de 600 a 500
    
    def setup_table(self):
        """Configura la tabla inicial"""
        # Configurar filas (procesos)
        procesos = self.resultado.procesos
        self.tabla.setRowCount(len(procesos))
        
        # Configurar columnas (ciclos)
        ciclos_totales = min(self.resultado.ciclos_totales, 50)  # Limitar columnas
        self.tabla.setColumnCount(ciclos_totales)
        
        # Headers de filas (PIDs)
        row_headers = [proceso.pid for proceso in procesos]
        self.tabla.setVerticalHeaderLabels(row_headers)
        
        # Headers de columnas (ciclos)
        col_headers = [str(c) for c in range(ciclos_totales)]
        self.tabla.setHorizontalHeaderLabels(col_headers)
        
        # Ajustar tamaños
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        for i in range(ciclos_totales):
            self.tabla.setColumnWidth(i, 80)
        
        # Inicializar celdas vacías
        for fila in range(len(procesos)):
            for columna in range(ciclos_totales):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, columna, item)
    
    def init_timer(self):
        """Inicializa el timer para la animación"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tabla)
        self.timer.start(1200)  # Actualiza cada 1.2 segundos
    
    def actualizar_tabla(self):
        """Actualiza la tabla con el siguiente ciclo"""
        if self.ciclo_actual >= self.resultado.ciclos_totales:
            self.timer.stop()
            self.label_ciclo.setText(f"Simulación completada - Ciclos totales: {self.resultado.ciclos_totales}")
            return
        
        self.mostrar_ciclo(self.ciclo_actual)
        self.ciclo_actual += 1
    
    def mostrar_ciclo(self, ciclo):
        """Muestra la información de un ciclo específico"""
        # Actualizar etiqueta de ciclo
        self.label_ciclo.setText(f"Ciclo actual: {ciclo}")
        
        # Actualizar información de recursos
        recursos_info = "Recursos: "
        for recurso in self.resultado.recursos.values():
            recursos_info += f"{recurso.nombre}({recurso.contador_actual}/{recurso.contador_inicial}) "
        self.label_recursos.setText(recursos_info)
        
        # Actualizar tabla si hay información para este ciclo
        if ciclo in self.resultado.tabla_estados:
            estados_ciclo = self.resultado.tabla_estados[ciclo]
            detalle_texto = f"CICLO {ciclo}:\n"
            
            for i, proceso in enumerate(self.resultado.procesos):
                if proceso.pid in estados_ciclo:
                    info = estados_ciclo[proceso.pid]
                    estado = info['estado']
                    tiempo_restante = info['tiempo_restante']
                    
                    # Crear texto para la celda
                    if estado == "FINISHED":
                        texto = "FIN"
                    elif estado == "BLOCKED":
                        recurso_esp = info.get('recurso_esperando', '')
                        texto = f"WAIT\n{recurso_esp}"
                    elif estado == "RUNNING":
                        recursos_usando = info.get('recursos_usando', [])
                        if recursos_usando:
                            texto = f"RUN\n{','.join(recursos_usando)}"
                        else:
                            texto = f"RUN\n({tiempo_restante})"
                    else:
                        texto = estado
                    
                    # Actualizar celda si está dentro del rango de columnas
                    if ciclo < self.tabla.columnCount():
                        item = self.tabla.item(i, ciclo)
                        item.setText(texto)
                        
                        # Aplicar color según estado
                        color = self.colores_estado.get(estado, QColor(255, 255, 255))
                        item.setBackground(QBrush(color))
                    
                    # Agregar al detalle
                    detalle_texto += f"  {proceso.pid}: {estado}"
                    if info.get('recurso_esperando'):
                        detalle_texto += f" (esperando {info['recurso_esperando']})"
                    elif info.get('recursos_usando'):
                        detalle_texto += f" (usando {', '.join(info['recursos_usando'])})"
                    detalle_texto += f" [TR: {tiempo_restante}]\n"
            
            # Actualizar área de detalle
            self.texto_detalle.setPlainText(detalle_texto)
    
    def pausar_animacion(self):
        """Pausa la animación"""
        self.timer.stop()
    
    def reanudar_animacion(self):
        """Reanuda la animación"""
        if self.ciclo_actual < self.resultado.ciclos_totales:
            self.timer.start(1200)
    
    def siguiente_ciclo(self):
        """Avanza al siguiente ciclo manualmente"""
        if self.ciclo_actual < self.resultado.ciclos_totales:
            self.mostrar_ciclo(self.ciclo_actual)
            self.ciclo_actual += 1
    
    def reiniciar_animacion(self):
        """Reinicia la animación"""
        self.timer.stop()
        self.ciclo_actual = 0
        self.setup_table()
        self.timer.start(1200)