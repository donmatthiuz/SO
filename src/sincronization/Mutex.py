import copy
from src.sincronization.resultado import ResultadoSincronizacion
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
                    
                  
                    proceso_liberado = recurso.liberar_de_proceso(proceso)
                    
                    # Remover la acción de las acciones en curso del proceso
                    if hasattr(proceso, 'acciones_en_curso'):
                        proceso.acciones_en_curso = [a for a in proceso.acciones_en_curso if a != accion]
                    
                    # Si se liberó el recurso para otro proceso, actualizar su estado
                    if proceso_liberado:
                        proceso_liberado.estado = "ACCESED"
                        proceso_liberado.recurso_esperando = None
        
        # Actualizar estados de todos los procesos activos
        for proceso in procesos_activos[:]:
            # Verificar si el proceso está realizando alguna acción
            realizando_accion = (hasattr(proceso, 'acciones_en_curso') and 
                               len(proceso.acciones_en_curso) > 0)
            
            # Si el proceso no está bloqueado y no está realizando una acción específica
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
                    
                    # Liberar todos los recursos que tenía
                    for recurso in recursos_copia.values():
                        proceso_liberado = recurso.liberar_de_proceso(proceso)
                        if proceso_liberado:
                            proceso_liberado.estado = "ACCESED"
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
                            proceso_liberado.estado = "ACCESED"
                            proceso_liberado.recurso_esperando = None
            
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
        if not procesos_activos and not acciones_pendientes and ciclo_actual > max([p.tiempo_llegada for p in procesos_copia]):
            break
    
    return ResultadoSincronizacion(procesos_copia, recursos_copia, tabla_estados, ciclo_actual)

