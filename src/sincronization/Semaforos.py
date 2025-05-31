import copy
from src.sincronization.resultado import ResultadoSincronizacion

def simular_sincronizacion_semaforos(procesos, recursos, acciones):
    """Simula la sincronización de procesos con semáforos"""
    
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
    max_tiempo_cpu = max([p.tiempo_cpu + p.tiempo_llegada for p in procesos_copia])
    ciclos_totales = max(max_ciclo_acciones + 15, max_tiempo_cpu + 10)
    
    while ciclo_actual < ciclos_totales:
        # Inicializar estado del ciclo
        tabla_estados[ciclo_actual] = {}
        
        # Agregar procesos que llegan en este ciclo
        for proceso in procesos_copia:
            if proceso.tiempo_llegada == ciclo_actual:
                procesos_activos.append(proceso)
                proceso.estado = "ACCESED"
                if proceso.tiempo_inicio is None:
                    proceso.tiempo_inicio = ciclo_actual
        
        # Procesar acciones programadas para este ciclo
        acciones_ciclo = [a for a in acciones_copia if a.ciclo == ciclo_actual and not a.ejecutada]
        
        for accion in acciones_ciclo:
            # Buscar el proceso
            proceso = next((p for p in procesos_activos if p.pid == accion.pid), None)
            if proceso and accion.recurso in recursos_copia:
                recurso = recursos_copia[accion.recurso]
                
                # Para semáforos, verificar si el proceso puede hacer wait() en el semáforo
                if proceso.estado != "BLOCKED" or proceso.recurso_esperando == accion.recurso:
                    
                    # Operación WAIT (P) en el semáforo
                    if accion.accion in ["read", "write"]:
                        if recurso.wait_semaforo(proceso):
                            # El proceso obtiene el recurso y comienza la acción
                            proceso.estado = "RUNNING"
                            proceso.recurso_esperando = None
                            accion.ejecutada = True
                            accion.ciclo_inicio = ciclo_actual
                            
                            # Determinar duración de la acción (lectura: 2 ciclos, escritura: 3 ciclos)
                            duracion = 2 if accion.accion == "read" else 3
                            accion.ciclo_fin = ciclo_actual + duracion
                            
                            # Marcar que el proceso está usando este recurso para esta acción
                            if not hasattr(proceso, 'acciones_en_curso'):
                                proceso.acciones_en_curso = []
                            proceso.acciones_en_curso.append(accion)
                            
                        else:
                            # El semáforo está en 0, el proceso debe esperar
                            proceso.estado = "BLOCKED"
                            proceso.recurso_esperando = accion.recurso
                            # Agregar a la cola de espera del semáforo
                            if not hasattr(recurso, 'cola_espera'):
                                recurso.cola_espera = []
                            if proceso not in recurso.cola_espera:
                                recurso.cola_espera.append(proceso)
        
        # Procesar liberación de recursos por acciones completadas
        for accion in acciones_copia:
            if (accion.ejecutada and hasattr(accion, 'ciclo_fin') and 
                accion.ciclo_fin == ciclo_actual):
                
                # Buscar el proceso que completó la acción
                proceso = next((p for p in procesos_activos if p.pid == accion.pid), None)
                if proceso and accion.recurso in recursos_copia:
                    recurso = recursos_copia[accion.recurso]
                    
                    # Operación SIGNAL (V) en el semáforo
                    proceso_desbloqueado = recurso.signal_semaforo(proceso)
                    
                    # Remover la acción de las acciones en curso del proceso
                    if hasattr(proceso, 'acciones_en_curso'):
                        proceso.acciones_en_curso = [a for a in proceso.acciones_en_curso if a != accion]
                    
                    # Si se desbloqueó otro proceso, actualizar su estado
                    if proceso_desbloqueado:
                        proceso_desbloqueado.estado = "ACCESED"
                        proceso_desbloqueado.recurso_esperando = None
        
        # Actualizar estados de todos los procesos activos
        for proceso in procesos_activos[:]:
            # Verificar si el proceso está realizando alguna acción
            realizando_accion = (hasattr(proceso, 'acciones_en_curso') and 
                               len(proceso.acciones_en_curso) > 0)
            
            # Si el proceso está listo y no está realizando una acción específica
            if proceso.estado == "ACCESED" and proceso.tiempo_restante > 0 and not realizando_accion:
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
                    
                    # Liberar todos los semáforos que tenía
                    for recurso in recursos_copia.values():
                        if hasattr(recurso, 'procesos_usando') and proceso in recurso.procesos_usando:
                            proceso_desbloqueado = recurso.signal_semaforo(proceso)
                            if proceso_desbloqueado:
                                proceso_desbloqueado.estado = "ACCESED"
                                proceso_desbloqueado.recurso_esperando = None
            
            # Si el proceso está realizando una acción, también reduce su tiempo restante
            elif realizando_accion and proceso.estado == "RUNNING":
                # El proceso está usando tiempo mientras realiza la acción
                proceso.tiempo_restante -= 1
                proceso.ciclos_ejecutados += 1
                
                # Verificar si termina
                if proceso.tiempo_restante <= 0:
                    proceso.estado = "FINISHED"
                    proceso.tiempo_fin = ciclo_actual + 1
                    
                    # Liberar todos los semáforos que tenía
                    for recurso in recursos_copia.values():
                        if hasattr(recurso, 'procesos_usando') and proceso in recurso.procesos_usando:
                            proceso_desbloqueado = recurso.signal_semaforo(proceso)
                            if proceso_desbloqueado:
                                proceso_desbloqueado.estado = "ACCESED"
                                proceso_desbloqueado.recurso_esperando = None
            
            # Registrar estado del proceso en este ciclo
            estado_info = {
                'proceso': proceso,
                'estado': proceso.estado,
                'tiempo_restante': proceso.tiempo_restante,
                'recurso_esperando': proceso.recurso_esperando,
                'recursos_usando': [],
                'accion_actual': None,
            }
            
            # Determinar qué recursos está usando
            for recurso in recursos_copia.values():
                if hasattr(recurso, 'procesos_usando') and proceso in recurso.procesos_usando:
                    estado_info['recursos_usando'].append(recurso.nombre)
            
            # Determinar si está realizando alguna acción
            if hasattr(proceso, 'acciones_en_curso') and proceso.acciones_en_curso:
                accion_actual = proceso.acciones_en_curso[0]  # Tomar la primera acción en curso
                estado_info['accion_actual'] = f"{accion_actual.accion} {accion_actual.recurso}"
            
            tabla_estados[ciclo_actual][proceso.pid] = estado_info
        
        # Intentar desbloquear procesos que están esperando semáforos
        for proceso in procesos_activos:
            if proceso.estado == "BLOCKED" and proceso.recurso_esperando:
                recurso = recursos_copia[proceso.recurso_esperando]
                
                                        # Verificar si el proceso está en la cola y puede obtener el semáforo
                if (hasattr(recurso, 'cola_espera') and proceso in recurso.cola_espera and
                    recurso.contador_actual > 0):
                    
                    # Buscar si hay una acción pendiente para este proceso y recurso
                    accion_pendiente = next((a for a in acciones_copia 
                                           if a.pid == proceso.pid and 
                                              a.recurso == proceso.recurso_esperando and 
                                              a.ciclo <= ciclo_actual and not a.ejecutada), None)
                    
                    if accion_pendiente and recurso.wait_semaforo(proceso):
                        recurso.cola_espera.remove(proceso)
                        proceso.estado = "RUNNING"
                        proceso.recurso_esperando = None
                        accion_pendiente.ejecutada = True
                        accion_pendiente.ciclo_inicio = ciclo_actual
                        
                        duracion = 2 if accion_pendiente.accion == "read" else 3
                        accion_pendiente.ciclo_fin = ciclo_actual + duracion
                        
                        if not hasattr(proceso, 'acciones_en_curso'):
                            proceso.acciones_en_curso = []
                        proceso.acciones_en_curso.append(accion_pendiente)
        
        # Remover procesos terminados de la lista activa
        procesos_activos = [p for p in procesos_activos if p.estado != "FINISHED"]
        
        ciclo_actual += 1
        
        # Verificar si todos los procesos han terminado y no hay acciones pendientes
        acciones_pendientes = any(not a.ejecutada for a in acciones_copia)
        if not procesos_activos and not acciones_pendientes and ciclo_actual > max([p.tiempo_llegada for p in procesos_copia]):
            break
    
    return ResultadoSincronizacion(procesos_copia, recursos_copia, tabla_estados, ciclo_actual)


# Clase Semáforo para manejar la sincronización
class Semaforo:
    def __init__(self, nombre, valor_inicial=1):
        self.nombre = nombre
        self.valor_semaforo = valor_inicial
        self.valor_inicial = valor_inicial
        self.procesos_usando = []
        self.cola_espera = []
    
    def wait_semaforo(self, proceso):
        """Operación WAIT (P) en el semáforo"""
        if self.valor_semaforo > 0:
            self.valor_semaforo -= 1
            if proceso not in self.procesos_usando:
                self.procesos_usando.append(proceso)
            return True
        else:
            # Semáforo en 0, el proceso debe esperar
            if proceso not in self.cola_espera:
                self.cola_espera.append(proceso)
            return False
    
    def signal_semaforo(self, proceso):
        """Operación SIGNAL (V) en el semáforo"""
        # Remover el proceso de los que están usando el semáforo
        if proceso in self.procesos_usando:
            self.procesos_usando.remove(proceso)
        
        self.valor_semaforo += 1
        
        # Si hay procesos esperando, despertar al primero
        if self.cola_espera and self.valor_semaforo > 0:
            proceso_desbloqueado = self.cola_espera.pop(0)
            self.valor_semaforo -= 1
            if proceso_desbloqueado not in self.procesos_usando:
                self.procesos_usando.append(proceso_desbloqueado)
            return proceso_desbloqueado
        
        return None
    
    def esta_disponible(self):
        """Verifica si el semáforo tiene valor mayor a 0"""
        return self.valor_semaforo > 0
    
    def get_estado(self):
        """Retorna el estado actual del semáforo"""
        return {
            'valor': self.valor_semaforo,
            'procesos_usando': [p.pid for p in self.procesos_usando],
            'cola_espera': [p.pid for p in self.cola_espera]
        }