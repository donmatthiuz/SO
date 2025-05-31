
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QPushButton, QTextEdit, 
                             QHeaderView, QTabWidget)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QBrush

class SyncTableWindow(QWidget):
    def __init__(self, resultado_sincronizacion, parent=None):
        super().__init__(parent)
        self.resultado = resultado_sincronizacion
        self.ciclo_actual = 0
        
        # Colores actualizados para semáforos
        self.colores_estado = {
            "READY": QColor(100, 200, 100),       # Verde claro - Listo para ejecutar
            "RUNNING": QColor(100, 150, 255),     # Azul - Ejecutándose
            "BLOCKED": QColor(255, 150, 100),     # Naranja - Bloqueado esperando semáforo
            "FINISHED": QColor(200, 200, 200),    # Gris - Terminado
            "WAITING": QColor(255, 255, 150),     # Amarillo - Esperando (alternativo)
            "ACCESED": QColor(150, 255, 150)      # Verde - Accesible (para compatibilidad)
        }
        
        self.init_ui()
        self.setup_table()
        self.init_timer()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Etiqueta de título
        self.label_titulo = QLabel("Simulación de Sincronizacion", self)
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        
        # Etiqueta de ciclo actual
        self.label_ciclo = QLabel(f"Ciclo actual: {self.ciclo_actual}", self)
        self.label_ciclo.setAlignment(Qt.AlignCenter)
        self.label_ciclo.setStyleSheet("font-size: 14px; margin: 5px;")
        
        # Información de semáforos
        self.label_semaforos = QLabel("", self)
        self.label_semaforos.setAlignment(Qt.AlignCenter)
        self.label_semaforos.setStyleSheet("font-size: 12px; margin: 5px; background-color: #f0f0f0; padding: 5px;")
        
        # Crear pestañas para diferentes vistas
        self.tabs = QTabWidget()
        
        # Pestaña 1: Vista principal de procesos
        tab_procesos = QWidget()
        layout_procesos = QHBoxLayout(tab_procesos)
        
        # Tabla principal
        self.tabla = QTableWidget(self)
        
        # Área de información detallada
        self.texto_detalle = QTextEdit(self)
        self.texto_detalle.setMinimumWidth(350)
        self.texto_detalle.setMaximumWidth(450)
        self.texto_detalle.setReadOnly(True)
        
        layout_procesos.addWidget(self.tabla, 2)
        layout_procesos.addWidget(self.texto_detalle, 1)
        
        # Pestaña 2: Vista de semáforos
        tab_semaforos = QWidget()
        layout_semaforos = QVBoxLayout(tab_semaforos)
        
        self.texto_semaforos = QTextEdit(self)
        self.texto_semaforos.setReadOnly(True)
        self.texto_semaforos.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout_semaforos.addWidget(self.texto_semaforos)
        
        # Agregar pestañas
        self.tabs.addTab(tab_procesos, "Vista de Procesos")
        self.tabs.addTab(tab_semaforos, "Vista de Semáforos")
        
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
        
        # Leyenda de colores
        leyenda_layout = QHBoxLayout()
        leyenda_label = QLabel("Leyenda: ")
        leyenda_layout.addWidget(leyenda_label)
        
        for estado, color in self.colores_estado.items():
            if estado in ["READY", "RUNNING", "BLOCKED", "FINISHED"]:
                label = QLabel(estado)
                label.setStyleSheet(f"background-color: {color.name()}; padding: 2px 8px; margin: 2px; border: 1px solid black;")
                leyenda_layout.addWidget(label)
        
        leyenda_layout.addStretch()
        
        # Agregar widgets al layout principal
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_ciclo)
        layout.addWidget(self.label_semaforos)
        layout.addWidget(self.tabs)
        layout.addLayout(leyenda_layout)
        layout.addLayout(controles_layout)
        
        # Conectar botones
        self.btn_pausar.clicked.connect(self.pausar_animacion)
        self.btn_reanudar.clicked.connect(self.reanudar_animacion)
        self.btn_reiniciar.clicked.connect(self.reiniciar_animacion)
        self.btn_siguiente.clicked.connect(self.siguiente_ciclo)
        
        self.setLayout(layout)
        self.setWindowTitle("Simulación de Semáforos")
        self.resize(1400, 400)
    
    def setup_table(self):
        """Configura la tabla inicial"""
        # Configurar filas (procesos)
        procesos = self.resultado.procesos
        self.tabla.setRowCount(len(procesos))
        
        # Configurar columnas (ciclos)
        ciclos_totales = min(self.resultado.ciclos_totales, 50)
        self.tabla.setColumnCount(ciclos_totales)
        
        # Headers de filas (PIDs)
        row_headers = [f"P{proceso.pid}" for proceso in procesos]
        self.tabla.setVerticalHeaderLabels(row_headers)
        
        # Headers de columnas (ciclos)
        col_headers = [str(c) for c in range(ciclos_totales)]
        self.tabla.setHorizontalHeaderLabels(col_headers)
        
        # Ajustar tamaños
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        for i in range(len(procesos)):
            self.tabla.setRowHeight(i, 70)  # Un poco más alto para mostrar más información
        
        for i in range(ciclos_totales):
            self.tabla.setColumnWidth(i, 140)  # Un poco más ancho
        
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
        self.timer.start(1500)  # Un poco más lento para poder leer mejor
    
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
        
        
        
        # Actualizar tabla si hay información para este ciclo
        if ciclo in self.resultado.tabla_estados:
            estados_ciclo = self.resultado.tabla_estados[ciclo]
            detalle_texto = f"=== CICLO {ciclo} ===\n\n"
            semaforos_texto = f"=== ESTADO DE SEMÁFOROS - CICLO {ciclo} ===\n\n"
            
            # Información detallada de semáforos
            for nombre, recurso in self.resultado.recursos.items():
                estado_sem = recurso.get_estado_semaforo()
                semaforos_texto += f"{nombre}:\n"
                semaforos_texto += f"  Valor actual: {estado_sem['valor']}\n"
                semaforos_texto += f"  Procesos usando: {estado_sem['procesos_usando']}\n"
                semaforos_texto += f"  Cola de espera: {estado_sem['cola_espera']}\n\n"
            
            # Información de procesos
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
                        texto = f"BLOCKED\n{recurso_esp}\n({tiempo_restante})"
                    elif estado == "RUNNING":
                        recursos_usando = info.get('recursos_usando', [])
                        accion_actual = info.get('accion_actual', '')
                        if accion_actual:
                            texto = f"RUN\n{accion_actual}\n({tiempo_restante})"
                        elif recursos_usando:
                            texto = f"RUN\n{','.join(recursos_usando)}\n({tiempo_restante})"
                        else:
                            texto = f"RUN\n({tiempo_restante})"
                    elif estado == "READY":
                        texto = f"READY\n({tiempo_restante})"
                    else:
                        texto = f"{estado}\n({tiempo_restante})"
                    
                    # Actualizar celda si está dentro del rango de columnas
                    if ciclo < self.tabla.columnCount():
                        item = self.tabla.item(i, ciclo)
                        item.setText(texto)
                        
                        # Aplicar color según estado
                        color = self.colores_estado.get(estado, QColor(255, 255, 255))
                        item.setBackground(QBrush(color))
                    
                    # Agregar al detalle
                    detalle_texto += f"P{proceso.pid}: {estado}"
                    if info.get('recurso_esperando'):
                        detalle_texto += f" (esperando {info['recurso_esperando']})"
                    if info.get('recursos_usando'):
                        detalle_texto += f" (usando {', '.join(info['recursos_usando'])})"
                    if info.get('accion_actual'):
                        detalle_texto += f" [{info['accion_actual']}]"
                    detalle_texto += f" TR:{tiempo_restante}\n"
            
            # Agregar información de semáforos al detalle
            detalle_texto += "\nSEMÁFOROS:\n"
            for nombre, recurso in self.resultado.recursos.items():
                estado_sem = recurso.get_estado_semaforo()
                detalle_texto += f"{nombre}: V={estado_sem['valor']} U={estado_sem['procesos_usando']} E={estado_sem['cola_espera']}\n"
            
            # Actualizar áreas de texto
            self.texto_detalle.setPlainText(detalle_texto)
            self.texto_semaforos.setPlainText(semaforos_texto)
    
    def pausar_animacion(self):
        """Pausa la animación"""
        self.timer.stop()
    
    def reanudar_animacion(self):
        """Reanuda la animación"""
        if self.ciclo_actual < self.resultado.ciclos_totales:
            self.timer.start(1500)
    
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
        self.timer.start(1500)
