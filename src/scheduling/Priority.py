import copy
from src.scheduling.resultados import ResultadoSimulacion
from src.scheduling.AlgoritmoPlanificacion import AlgoritmoPlanificacion

class Priority(AlgoritmoPlanificacion):
    def simular(self):
        procesos_copia = copy.deepcopy(self.procesos)
        tiempo_actual = 0
        procesos_completados = []
        tabla_ejecucion = {}
        
        # Ordenar inicialmente por tiempo de llegada
        procesos_copia.sort(key=lambda p: p.tiempo_llegada)
        
        while len(procesos_completados) < len(procesos_copia):
            # Filtrar procesos listos usando IDs para evitar problemas de comparación
            procesos_completados_ids = {p.id if hasattr(p, 'id') else id(p) for p in procesos_completados}
            listos = [
                p for p in procesos_copia
                if (p.tiempo_llegada <= tiempo_actual and 
                    (p.id if hasattr(p, 'id') else id(p)) not in procesos_completados_ids)
            ]
            
            if not listos:
                # Saltar al próximo tiempo de llegada
                proximos_tiempos = [
                    p.tiempo_llegada for p in procesos_copia 
                    if (p.id if hasattr(p, 'id') else id(p)) not in procesos_completados_ids
                ]
                if proximos_tiempos:
                    tiempo_actual = min(proximos_tiempos)
                continue
            
            # Debug: Mostrar procesos listos y sus prioridades
          
            for p in listos:
                nombre = p.nombre if hasattr(p, 'nombre') else f"Proceso_{id(p)}"
               
            # Escoger el de mayor prioridad (número más bajo = más alta prioridad)
            actual = min(listos, key=lambda p: p.prioridad)
            nombre_actual = actual.nombre if hasattr(actual, 'nombre') else f"Proceso_{id(actual)}"
           
            
            # Asignar tiempos
            actual.tiempo_inicio = tiempo_actual
            actual.tiempo_fin = tiempo_actual + actual.tiempo_cpu
            actual.tiempo_espera = actual.tiempo_inicio - actual.tiempo_llegada
            actual.tiempo_respuesta = actual.tiempo_espera
            
            # Registrar ejecución en la tabla
            tiempo_inicio_ejecucion = tiempo_actual
            for i in range(actual.tiempo_cpu):
                tiempo_slot = tiempo_inicio_ejecucion + i
                tiempo_restante = actual.tiempo_cpu - i - 1
                estado = "EJECUTANDO" if tiempo_restante > 0 else "TERMINADO"
                
                tabla_ejecucion[tiempo_slot] = {
                    'proceso': actual,
                    'estado': estado,
                    'tiempo_restante': tiempo_restante
                }
            
            # Actualizar tiempo actual
            tiempo_actual = actual.tiempo_fin
            procesos_completados.append(actual)
        
        return ResultadoSimulacion(procesos_copia, tabla_ejecucion, tiempo_actual)