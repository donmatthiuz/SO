import copy

from src.scheduling.resultados import ResultadoSimulacion
from src.scheduling.AlgoritmoPlanificacion import AlgoritmoPlanificacion

class SJF(AlgoritmoPlanificacion):
    def simular(self):
        procesos_copia = copy.deepcopy(self.procesos)
       
        procesos_copia.sort(key=lambda p: p.tiempo_llegada)
        
        tiempo_actual = 0
        tabla_ejecucion = {}
        procesos_completados = []
        procesos_listos = []
        
        
        while len(procesos_completados) < len(procesos_copia):
           
            for proceso in procesos_copia:
                if (proceso.tiempo_llegada <= tiempo_actual and 
                    proceso not in procesos_completados and 
                    proceso not in procesos_listos):
                    procesos_listos.append(proceso)
            
            if procesos_listos:
                
                proceso_actual = min(procesos_listos, key=lambda p: p.tiempo_cpu)
                procesos_listos.remove(proceso_actual)
                
                
                if proceso_actual.tiempo_inicio is None:
                    proceso_actual.tiempo_inicio = tiempo_actual
                    proceso_actual.tiempo_respuesta = tiempo_actual - proceso_actual.tiempo_llegada
                
              
                for i in range(proceso_actual.tiempo_cpu):
                    estado = "EJECUTANDO"
                    if i == proceso_actual.tiempo_cpu - 1:
                        estado = "TERMINADO"
                        proceso_actual.tiempo_fin = tiempo_actual + 1
                    
                    tabla_ejecucion[tiempo_actual] = {
                        'proceso': proceso_actual,
                        'estado': estado,
                        'tiempo_restante': proceso_actual.tiempo_cpu - i - 1
                    }
                    tiempo_actual += 1
                
                # Calcular tiempo de espera
                proceso_actual.tiempo_espera = proceso_actual.tiempo_inicio - proceso_actual.tiempo_llegada
                procesos_completados.append(proceso_actual)
            else:
                # Si no hay procesos listos, avanzar el tiempo hasta la próxima llegada
                proxima_llegada = min(
                    [p.tiempo_llegada for p in procesos_copia 
                     if p not in procesos_completados and p.tiempo_llegada > tiempo_actual],
                    default=tiempo_actual
                )
                if proxima_llegada > tiempo_actual:
                    tiempo_actual = proxima_llegada
        
        return ResultadoSimulacion(procesos_copia, tabla_ejecucion, tiempo_actual)