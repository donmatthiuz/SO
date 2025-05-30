# main.py
import sys
from PyQt5.QtWidgets import QApplication


# ===================================

# gui.py
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QHBoxLayout, QTextEdit)
from PyQt5.QtCore import Qt

class SimuladorSincronizacionGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        # Widget central
        central = QWidget(self)
        layout = QVBoxLayout(central)
        
        # Título
        titulo = QLabel("Simulador de Sincronización con Mutex", self)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        
        # Área de información
        info_layout = QHBoxLayout()
        
        # Información de archivos
        info_text = QTextEdit(self)
        info_text.setMaximumHeight(120)
        info_text.setPlainText("""Archivos necesarios en carpeta 'data/':
- procesos.txt: PID, BT, AT, Priority (ej: P1, 8, 0, 1)
- recursos.txt: NOMBRE_RECURSO, CONTADOR (ej: R1, 1)
- acciones.txt: PID, ACCION, RECURSO, CICLO (ej: P1, READ, R1, 0)""")
        info_text.setReadOnly(True)
        
        info_layout.addWidget(info_text)
        
        # Botones
        self.btn_simular = QPushButton("Iniciar Simulación", self)
        self.btn_simular.setStyleSheet("font-size: 14px; padding: 10px;")
        
        # Agregar widgets al layout
        layout.addWidget(titulo)
        layout.addLayout(info_layout)
        layout.addWidget(self.btn_simular)
        
        # Conectar señales
        self.btn_simular.clicked.connect(self.on_simular_clicked)
        
        self.setCentralWidget(central)
        self.setWindowTitle("Simulador de Sincronización")
        self.resize(600, 300)
    
    def on_simular_clicked(self):
        try:
            # Cargar datos
            procesos = cargar_procesos_desde_archivo("data/procesos.txt")
            recursos = cargar_recursos_desde_archivo("data/recursos.txt")
            acciones = cargar_acciones_desde_archivo("data/acciones.txt")
            
            if not procesos:
                QMessageBox.warning(self, "Error", "No se cargaron procesos.")
                return
            
            if not recursos:
                QMessageBox.warning(self, "Error", "No se cargaron recursos.")
                return
                
            if not acciones:
                QMessageBox.warning(self, "Error", "No se cargaron acciones.")
                return
            
            # Ejecutar simulación
            resultado_simulacion = simular_sincronizacion(procesos, recursos, acciones)
            
            # Mostrar tabla de sincronización
            self.sync_window = SyncTableWindow(resultado_simulacion, self)
            self.sync_window.show()
            
            # Mostrar estadísticas
            estadisticas = generar_estadisticas_sync(resultado_simulacion)
            msg = QMessageBox(self)
            msg.setWindowTitle("Estadísticas de Sincronización")
            msg.setText(estadisticas)
            msg.setDetailedText(generar_detalle_completo(resultado_simulacion))
            msg.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la simulación: {str(e)}")


# ===================================

# proceso_sync.py
class ProcesoSync:
    def __init__(self, pid, burst_time, arrival_time, priority):
        self.pid = pid
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.priority = priority
        self.tiempo_restante = burst_time
        self.tiempo_inicio = None
        self.tiempo_fin = None
        self.estado = "WAITING"  # WAITING, RUNNING, BLOCKED, FINISHED
        self.recurso_esperando = None
        self.ciclos_ejecutados = 0
    
    def __str__(self):
        return f"Proceso({self.pid}, BT:{self.burst_time}, AT:{self.arrival_time}, P:{self.priority})"

class Recurso:
    def __init__(self, nombre, contador):
        self.nombre = nombre
        self.contador_inicial = contador
        self.contador_actual = contador
        self.procesos_usando = []  # Lista de procesos que están usando el recurso
        self.cola_espera = []      # Cola de procesos esperando el recurso
    
    def esta_disponible(self):
        return self.contador_actual > 0
    
    def asignar_a_proceso(self, proceso):
        if self.esta_disponible():
            self.contador_actual -= 1
            self.procesos_usando.append(proceso)
            return True
        else:
            if proceso not in self.cola_espera:
                self.cola_espera.append(proceso)
            return False
    
    def liberar_de_proceso(self, proceso):
        if proceso in self.procesos_usando:
            self.procesos_usando.remove(proceso)
            self.contador_actual += 1
            
            # Asignar a siguiente proceso en cola si hay disponibilidad
            if self.cola_espera and self.esta_disponible():
                siguiente_proceso = self.cola_espera.pop(0)
                self.asignar_a_proceso(siguiente_proceso)
                return siguiente_proceso
        return None
    
    def __str__(self):
        return f"Recurso({self.nombre}, {self.contador_actual}/{self.contador_inicial})"

class Accion:
    def __init__(self, pid, accion, recurso, ciclo):
        self.pid = pid
        self.accion = accion.upper()  # READ, WRITE
        self.recurso = recurso
        self.ciclo = ciclo
        self.ejecutada = False
        self.ciclo_inicio = None
        self.ciclo_fin = None
    
    def __str__(self):
        return f"Accion({self.pid}, {self.accion}, {self.recurso}, ciclo:{self.ciclo})"

class ResultadoSincronizacion:
    def __init__(self, procesos, recursos, tabla_estados, ciclos_totales):
        self.procesos = procesos
        self.recursos = recursos
        self.tabla_estados = tabla_estados  # Dict[ciclo] -> Dict[proceso_pid] -> estado_info
        self.ciclos_totales = ciclos_totales

def cargar_procesos_desde_archivo(archivo):
    """Carga procesos desde un archivo de texto"""
    procesos = []
    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith('#'):
                    partes = [p.strip() for p in linea.split(',')]
                    if len(partes) >= 4:
                        pid = partes[0]
                        burst_time = int(partes[1])
                        arrival_time = int(partes[2])
                        priority = int(partes[3])
                        procesos.append(ProcesoSync(pid, burst_time, arrival_time, priority))
    except FileNotFoundError:
        # Procesos de ejemplo
        procesos = [
            ProcesoSync("P1", 8, 0, 1),
            ProcesoSync("P2", 4, 1, 2),
            ProcesoSync("P3", 6, 2, 3),
        ]
    except Exception as e:
        print(f"Error cargando procesos: {e}")
    
    return procesos

def cargar_recursos_desde_archivo(archivo):
    """Carga recursos desde un archivo de texto"""
    recursos = {}
    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith('#'):
                    partes = [p.strip() for p in linea.split(',')]
                    if len(partes) >= 2:
                        nombre = partes[0]
                        contador = int(partes[1])
                        recursos[nombre] = Recurso(nombre, contador)
    except FileNotFoundError:
        # Recursos de ejemplo
        recursos = {
            "R1": Recurso("R1", 1),
            "R2": Recurso("R2", 2),
        }
    except Exception as e:
        print(f"Error cargando recursos: {e}")
    
    return recursos

def cargar_acciones_desde_archivo(archivo):
    """Carga acciones desde un archivo de texto"""
    acciones = []
    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith('#'):
                    partes = [p.strip() for p in linea.split(',')]
                    if len(partes) >= 4:
                        pid = partes[0]
                        accion = partes[1]
                        recurso = partes[2]
                        ciclo = int(partes[3])
                        acciones.append(Accion(pid, accion, recurso, ciclo))
    except FileNotFoundError:
        # Acciones de ejemplo
        acciones = [
            Accion("P1", "read", "R1", 0),
            Accion("P2", "write", "R1", 1),
            Accion("P1", "write", "R2", 3),
            Accion("P3", "read", "R1", 2),
            Accion("P2", "read", "R2", 4),
        ]
    except Exception as e:
        print(f"Error cargando acciones: {e}")
    
    return acciones


# ===================================

# algoritmo_sync.py
import copy

def simular_sincronizacion(procesos, recursos, acciones):
    """Simula la sincronización de procesos con mutex"""
    
    procesos_copia = copy.deepcopy(procesos)
    recursos_copia = copy.deepcopy(recursos)
    acciones_copia = copy.deepcopy(acciones)
    
    # Ordenar acciones por ciclo
    acciones_copia.sort(key=lambda a: a.ciclo)
    
    ciclo_actual = 0
    tabla_estados = {}
    procesos_activos = []
    
    # Determinar ciclo máximo
    max_ciclo_acciones = max([a.ciclo for a in acciones_copia]) if acciones_copia else 0
    max_burst_time = max([p.burst_time + p.arrival_time for p in procesos_copia])
    ciclos_totales = max(max_ciclo_acciones + 15, max_burst_time + 10)
    
    while ciclo_actual < ciclos_totales:
        # Inicializar estado del ciclo
        tabla_estados[ciclo_actual] = {}
        
        # Agregar procesos que llegan en este ciclo
        for proceso in procesos_copia:
            if proceso.arrival_time == ciclo_actual:
                procesos_activos.append(proceso)
                proceso.estado = "READY"
                if proceso.tiempo_inicio is None:
                    proceso.tiempo_inicio = ciclo_actual
        
        # Procesar acciones programadas para este ciclo
        acciones_ciclo = [a for a in acciones_copia if a.ciclo == ciclo_actual and not a.ejecutada]
        
        for accion in acciones_ciclo:
            # Buscar el proceso
            proceso = next((p for p in procesos_activos if p.pid == accion.pid), None)
            if proceso and accion.recurso in recursos_copia:
                recurso = recursos_copia[accion.recurso]
                
                # Verificar si el proceso puede acceder al recurso
                if proceso.estado != "BLOCKED" or proceso.recurso_esperando == accion.recurso:
                    if recurso.asignar_a_proceso(proceso):
                        # El proceso obtiene el recurso y comienza la acción
                        proceso.estado = "RUNNING"
                        proceso.recurso_esperando = None
                        accion.ejecutada = True
                        accion.ciclo_inicio = ciclo_actual
                        
                        # Determinar duración de la acción (lectura: 2 ciclos, escritura: 3 ciclos)
                        duracion = 2 if accion.accion == "READ" else 3
                        accion.ciclo_fin = ciclo_actual + duracion
                        
                        # Marcar que el proceso está usando este recurso para esta acción
                        if not hasattr(proceso, 'acciones_en_curso'):
                            proceso.acciones_en_curso = []
                        proceso.acciones_en_curso.append(accion)
                        
                    else:
                        # El recurso está ocupado, el proceso debe esperar
                        proceso.estado = "BLOCKED"
                        proceso.recurso_esperando = accion.recurso
        
        # Procesar liberación de recursos por acciones completadas
        for accion in acciones_copia:
            if (accion.ejecutada and hasattr(accion, 'ciclo_fin') and 
                accion.ciclo_fin == ciclo_actual):
                
                # Buscar el proceso que completó la acción
                proceso = next((p for p in procesos_activos if p.pid == accion.pid), None)
                if proceso and accion.recurso in recursos_copia:
                    recurso = recursos_copia[accion.recurso]
                    
                    # Liberar el recurso
                    proceso_liberado = recurso.liberar_de_proceso(proceso)
                    
                    # Remover la acción de las acciones en curso del proceso
                    if hasattr(proceso, 'acciones_en_curso'):
                        proceso.acciones_en_curso = [a for a in proceso.acciones_en_curso if a != accion]
                    
                    # Si se liberó el recurso para otro proceso, actualizar su estado
                    if proceso_liberado:
                        proceso_liberado.estado = "READY"
                        proceso_liberado.recurso_esperando = None
        
        # Actualizar estados de todos los procesos activos
        for proceso in procesos_activos[:]:
            # Verificar si el proceso está realizando alguna acción
            realizando_accion = (hasattr(proceso, 'acciones_en_curso') and 
                               len(proceso.acciones_en_curso) > 0)
            
            # Si el proceso no está bloqueado y no está realizando una acción específica
            if proceso.estado == "READY" and proceso.tiempo_restante > 0 and not realizando_accion:
                # Verificar si hay acciones pendientes para este proceso en ciclos futuros
                tiene_acciones_pendientes = any(
                    a.pid == proceso.pid and not a.ejecutada and a.ciclo > ciclo_actual 
                    for a in acciones_copia
                )
                
                if not tiene_acciones_pendientes:
                    # El proceso puede ejecutarse normalmente
                    proceso.estado = "RUNNING"
            
            # Ejecutar proceso si está corriendo y no está realizando una acción específica
            if proceso.estado == "RUNNING" and not realizando_accion:
                proceso.tiempo_restante -= 1
                proceso.ciclos_ejecutados += 1
                
                # Verificar si termina
                if proceso.tiempo_restante <= 0:
                    proceso.estado = "FINISHED"
                    proceso.tiempo_fin = ciclo_actual + 1
                    
                    # Liberar todos los recursos que tenía
                    for recurso in recursos_copia.values():
                        proceso_liberado = recurso.liberar_de_proceso(proceso)
                        if proceso_liberado:
                            proceso_liberado.estado = "READY"
                            proceso_liberado.recurso_esperando = None
            
            # Si el proceso está realizando una acción, también reduce su tiempo restante
            elif realizando_accion and proceso.estado == "RUNNING":
                # El proceso está usando tiempo mientras realiza la acción
                proceso.tiempo_restante -= 1
                proceso.ciclos_ejecutados += 1
                
                # Verificar si termina
                if proceso.tiempo_restante <= 0:
                    proceso.estado = "FINISHED"
                    proceso.tiempo_fin = ciclo_actual + 1
                    
                    # Liberar todos los recursos que tenía
                    for recurso in recursos_copia.values():
                        proceso_liberado = recurso.liberar_de_proceso(proceso)
                        if proceso_liberado:
                            proceso_liberado.estado = "READY"
                            proceso_liberado.recurso_esperando = None
            
            # Registrar estado del proceso en este ciclo
            estado_info = {
                'proceso': proceso,
                'estado': proceso.estado,
                'tiempo_restante': proceso.tiempo_restante,
                'recurso_esperando': proceso.recurso_esperando,
                'recursos_usando': [],
                'accion_actual': None
            }
            
            # Determinar qué recursos está usando
            for recurso in recursos_copia.values():
                if proceso in recurso.procesos_usando:
                    estado_info['recursos_usando'].append(recurso.nombre)
            
            # Determinar si está realizando alguna acción
            if hasattr(proceso, 'acciones_en_curso') and proceso.acciones_en_curso:
                accion_actual = proceso.acciones_en_curso[0]  # Tomar la primera acción en curso
                estado_info['accion_actual'] = f"{accion_actual.accion} {accion_actual.recurso}"
            
            tabla_estados[ciclo_actual][proceso.pid] = estado_info
        
        # Intentar desbloquear procesos que están esperando recursos
        for proceso in procesos_activos:
            if proceso.estado == "BLOCKED" and proceso.recurso_esperando:
                recurso = recursos_copia[proceso.recurso_esperando]
                if recurso.esta_disponible():
                    # Buscar si hay una acción pendiente para este proceso y recurso en este ciclo
                    accion_pendiente = next((a for a in acciones_copia 
                                           if a.pid == proceso.pid and 
                                              a.recurso == proceso.recurso_esperando and 
                                              a.ciclo <= ciclo_actual and not a.ejecutada), None)
                    
                    if accion_pendiente:
                        if recurso.asignar_a_proceso(proceso):
                            proceso.estado = "RUNNING"
                            proceso.recurso_esperando = None
                            accion_pendiente.ejecutada = True
                            accion_pendiente.ciclo_inicio = ciclo_actual
                            
                            duracion = 2 if accion_pendiente.accion == "READ" else 3
                            accion_pendiente.ciclo_fin = ciclo_actual + duracion
                            
                            if not hasattr(proceso, 'acciones_en_curso'):
                                proceso.acciones_en_curso = []
                            proceso.acciones_en_curso.append(accion_pendiente)
        
        # Remover procesos terminados de la lista activa
        procesos_activos = [p for p in procesos_activos if p.estado != "FINISHED"]
        
        ciclo_actual += 1
        
        # Verificar si todos los procesos han terminado y no hay acciones pendientes
        acciones_pendientes = any(not a.ejecutada for a in acciones_copia)
        if not procesos_activos and not acciones_pendientes and ciclo_actual > max([p.arrival_time for p in procesos_copia]):
            break
    
    return ResultadoSincronizacion(procesos_copia, recursos_copia, tabla_estados, ciclo_actual)



def generar_estadisticas_sync(resultado):
    """Genera estadísticas de la simulación de sincronización"""
    procesos = resultado.procesos
    ciclos_totales = resultado.ciclos_totales
    
    if not procesos:
        return "No hay procesos para mostrar estadísticas."
    
    estadisticas = f"=== ESTADÍSTICAS DE SINCRONIZACIÓN ===\n"
    estadisticas += f"Ciclos totales de simulación: {ciclos_totales}\n"
    estadisticas += f"Número de procesos: {len(procesos)}\n"
    estadisticas += f"Número de recursos: {len(resultado.recursos)}\n\n"
    
    # Estadísticas por proceso
    procesos_terminados = [p for p in procesos if p.tiempo_fin is not None]
    if procesos_terminados:
        tiempo_total_promedio = sum(p.tiempo_fin - p.arrival_time for p in procesos_terminados) / len(procesos_terminados)
        estadisticas += f"Tiempo total promedio: {tiempo_total_promedio:.2f} ciclos\n\n"
    
    estadisticas += "=== DETALLES POR PROCESO ===\n"
    for proceso in procesos:
        estadisticas += f"{proceso.pid}: "
        estadisticas += f"Llegada={proceso.arrival_time}, "
        estadisticas += f"BurstTime={proceso.burst_time}, "
        estadisticas += f"Prioridad={proceso.priority}, "
        if proceso.tiempo_fin:
            estadisticas += f"Terminó en ciclo {proceso.tiempo_fin}, "
            estadisticas += f"Tiempo total={proceso.tiempo_fin - proceso.arrival_time}\n"
        else:
            estadisticas += "No terminó\n"
    
    return estadisticas

def generar_detalle_completo(resultado):
    """Genera un detalle completo ciclo por ciclo"""
    detalle = "=== DETALLE CICLO POR CICLO ===\n\n"
    
    for ciclo in range(min(resultado.ciclos_totales, 50)):  # Limitar a 50 ciclos para legibilidad
        if ciclo in resultado.tabla_estados:
            detalle += f"CICLO {ciclo}:\n"
            estados = resultado.tabla_estados[ciclo]
            
            for pid, info in estados.items():
                proceso = info['proceso']
                estado = info['estado']
                detalle += f"  {pid}: {estado}"
                
                if info['recurso_esperando']:
                    detalle += f" (esperando {info['recurso_esperando']})"
                elif info['recursos_usando']:
                    detalle += f" (usando {', '.join(info['recursos_usando'])})"
                
                detalle += f" [TR: {info['tiempo_restante']}]\n"
            
            # Estado de recursos
            detalle += "  Recursos: "
            for recurso in resultado.recursos.values():
                detalle += f"{recurso.nombre}({recurso.contador_actual}/{recurso.contador_inicial}) "
            detalle += "\n\n"
    
    return detalle


# ===================================

# sync_table_window.py
import random
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
            "READY": QColor(100, 200, 100),      # Verde claro
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
        self.label_titulo = QLabel("Simulación de Sincronización con Mutex", self)
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
        
        # Tabla principal
        self.tabla = QTableWidget(self)
        
        # Área de información detallada
        self.texto_detalle = QTextEdit(self)
        self.texto_detalle.setMaximumHeight(150)
        self.texto_detalle.setReadOnly(True)
        
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
        
        # Agregar widgets al layout
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_ciclo)
        layout.addWidget(self.label_recursos)
        layout.addWidget(self.tabla)
        layout.addWidget(self.texto_detalle)
        layout.addLayout(controles_layout)
        
        # Conectar botones
        self.btn_pausar.clicked.connect(self.pausar_animacion)
        self.btn_reanudar.clicked.connect(self.reanudar_animacion)
        self.btn_reiniciar.clicked.connect(self.reiniciar_animacion)
        self.btn_siguiente.clicked.connect(self.siguiente_ciclo)
        
        self.setLayout(layout)
        self.setWindowTitle("Tabla de Sincronización")
        self.resize(1000, 600)
    
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


# ===================================

# Crear archivos de ejemplo
"""
Crear carpeta 'data/' y archivos:

procesos.txt:
# PID, BT, AT, Priority
P1, 8, 0, 1
P2, 4, 1, 2
P3, 6, 2, 3
P4, 3, 3, 1

recursos.txt:
# NOMBRE_RECURSO, CONTADOR
R1, 1
R2, 2
R3, 1

acciones.txt:
# PID, ACCION, RECURSO, CICLO
P1, read, R1, 0
P2, write, R1, 1
P1, write, R2, 3
P3, read, R1, 2
P2, read, R2, 4
P4, write, R3, 3
P3, read, R2, 5
P1, read, R3, 6
"""

def main():
    app = QApplication(sys.argv)
    ventana = SimuladorSincronizacionGUI()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()