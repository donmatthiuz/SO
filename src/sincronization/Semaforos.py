from src.sincronization.resultado import ResultadoSincronizacion
import copy

def simular_sincronizacion_semaforos(procesos, recursos, acciones):
    """Simula la sincronización de procesos usando semáforos"""
    
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
                
                # Operación WAIT en el semáforo
                if accion.accion == "WAIT":
                    if recurso.wait_semaforo(proceso):
                        # El proceso obtiene el recurso
                        proceso.estado = "RUNNING"
                        accion.ejecutada = True
                        accion.ciclo_inicio = ciclo_actual
                        accion.ciclo_fin = ciclo_actual + 1  # WAIT toma 1 ciclo
                    else:
                        # El proceso debe esperar
                        proceso.estado = "BLOCKED"
                        proceso.recurso_esperando = accion.recurso
                
                # Operación SIGNAL en el semáforo
                elif accion.accion == "SIGNAL":
                    proceso_desbloqueado = recurso.signal_semaforo(proceso)
                    accion.ejecutada = True
                    accion.ciclo_inicio = ciclo_actual
                    accion.ciclo_fin = ciclo_actual + 1  # SIGNAL toma 1 ciclo
                    
                    # Si se desbloqueó un proceso, actualizarlo
                    if proceso_desbloqueado:
                        proceso_desbloqueado.estado = "READY"
                        proceso_desbloqueado.recurso_esperando = None
                
                # Operaciones READ/WRITE (requieren que el proceso tenga el recurso)
                elif accion.accion in ["READ", "WRITE"]:
                    # Verificar si el proceso tiene acceso al recurso
                    if proceso in recurso.procesos_usando or proceso.estado != "BLOCKED":
                        if proceso.estado != "BLOCKED":
                            proceso.estado = "RUNNING"
                            proceso.recurso_esperando = None
                            accion.ejecutada = True
                            accion.ciclo_inicio = ciclo_actual
                            
                            # Determinar duración de la acción
                            duracion = 2 if accion.accion == "READ" else 3
                            accion.ciclo_fin = ciclo_actual + duracion
                            
                            # Marcar que el proceso está usando este recurso para esta acción
                            if not hasattr(proceso, 'acciones_en_curso'):
                                proceso.acciones_en_curso = []
                            proceso.acciones_en_curso.append(accion)
                    else:
                        # El proceso no tiene el recurso, debe esperar
                        proceso.estado = "BLOCKED"
                        proceso.recurso_esperando = accion.recurso
        
        # Procesar finalización de acciones
        for accion in acciones_copia:
            if (accion.ejecutada and hasattr(accion, 'ciclo_fin') and 
                accion.ciclo_fin == ciclo_actual):
                
                proceso = next((p for p in procesos_activos if p.pid == accion.pid), None)
                if proceso:
                    # Remover la acción de las acciones en curso del proceso
                    if hasattr(proceso, 'acciones_en_curso'):
                        proceso.acciones_en_curso = [a for a in proceso.acciones_en_curso if a != accion]
                    
                    # Si era una operación READ/WRITE, el proceso sigue teniendo el recurso
                    # El recurso se libera solo con SIGNAL
        
        # Actualizar estados de todos los procesos activos
        for proceso in procesos_activos[:]:
            # Verificar si el proceso está realizando alguna acción
            realizando_accion = (hasattr(proceso, 'acciones_en_curso') and 
                               len(proceso.acciones_en_curso) > 0)
            
            # Si el proceso está listo y no está realizando una acción específica
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
                    
                    # Liberar todos los recursos que tenía automáticamente
                    for recurso in recursos_copia.values():
                        if proceso in recurso.procesos_usando:
                            proceso_desbloqueado = recurso.signal_semaforo(proceso)
                            if proceso_desbloqueado:
                                proceso_desbloqueado.estado = "READY"
                                proceso_desbloqueado.recurso_esperando = None
            
            # Si el proceso está realizando una acción, también reduce su tiempo restante
            elif realizando_accion and proceso.estado == "RUNNING":
                proceso.tiempo_restante -= 1
                proceso.ciclos_ejecutados += 1
                
                # Verificar si termina
                if proceso.tiempo_restante <= 0:
                    proceso.estado = "FINISHED"
                    proceso.tiempo_fin = ciclo_actual + 1
                    
                    # Liberar todos los recursos que tenía
                    for recurso in recursos_copia.values():
                        if proceso in recurso.procesos_usando:
                            proceso_desbloqueado = recurso.signal_semaforo(proceso)
                            if proceso_desbloqueado:
                                proceso_desbloqueado.estado = "READY"
                                proceso_desbloqueado.recurso_esperando = None
            
            # Registrar estado del proceso en este ciclo
            estado_info = {
                'proceso': proceso,
                'estado': proceso.estado,
                'tiempo_restante': proceso.tiempo_restante,
                'recurso_esperando': proceso.recurso_esperando,
                'recursos_usando': [],
                'accion_actual': None,
                'semaforos': {}  # Estado de los semáforos
            }
            
            # Determinar qué recursos está usando
            for recurso in recursos_copia.values():
                if proceso in recurso.procesos_usando:
                    estado_info['recursos_usando'].append(recurso.nombre)
                # Agregar estado del semáforo
                estado_info['semaforos'][recurso.nombre] = recurso.get_estado_semaforo()
            
            # Determinar si está realizando alguna acción
            if hasattr(proceso, 'acciones_en_curso') and proceso.acciones_en_curso:
                accion_actual = proceso.acciones_en_curso[0]
                estado_info['accion_actual'] = f"{accion_actual.accion} {accion_actual.recurso}"
            
            tabla_estados[ciclo_actual][proceso.pid] = estado_info
        
        # Intentar desbloquear procesos que están esperando recursos
        for proceso in procesos_activos:
            if proceso.estado == "BLOCKED" and proceso.recurso_esperando:
                recurso = recursos_copia[proceso.recurso_esperando]
                
                # Buscar si hay una acción WAIT pendiente para este proceso
                accion_pendiente = next((a for a in acciones_copia 
                                       if a.pid == proceso.pid and 
                                          a.recurso == proceso.recurso_esperando and 
                                          a.ciclo <= ciclo_actual and not a.ejecutada and
                                          a.accion == "WAIT"), None)
                
                if accion_pendiente and recurso.contador_actual > 0:
                    if recurso.wait_semaforo(proceso):
                        proceso.estado = "READY"
                        proceso.recurso_esperando = None
                        accion_pendiente.ejecutada = True
                        accion_pendiente.ciclo_inicio = ciclo_actual
                        accion_pendiente.ciclo_fin = ciclo_actual + 1
        
        # Remover procesos terminados de la lista activa
        procesos_activos = [p for p in procesos_activos if p.estado != "FINISHED"]
        
        ciclo_actual += 1
        
        # Verificar si todos los procesos han terminado y no hay acciones pendientes
        acciones_pendientes = any(not a.ejecutada for a in acciones_copia)
        if not procesos_activos and not acciones_pendientes and ciclo_actual > max([p.tiempo_llegada for p in procesos_copia]):
            break
    
    return ResultadoSincronizacion(procesos_copia, recursos_copia, tabla_estados, ciclo_actual)

