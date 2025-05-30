import copy
from src.scheduling.resultados import ResultadoSimulacion
from src.scheduling.AlgoritmoPlanificacion import AlgoritmoPlanificacion

class FIFO(AlgoritmoPlanificacion):
    def simular(self):
        procesos_copia = copy.deepcopy(self.procesos)
        procesos_copia.sort(key=lambda p: p.tiempo_llegada)
        
        tiempo_actual = 0
        tabla_ejecucion = {}
        
        for proceso in procesos_copia:
            if tiempo_actual < proceso.tiempo_llegada:
                tiempo_actual = proceso.tiempo_llegada
            
            if proceso.tiempo_inicio is None:
                proceso.tiempo_inicio = tiempo_actual
                proceso.tiempo_respuesta = tiempo_actual - proceso.tiempo_llegada
            
            for i in range(proceso.tiempo_cpu):
                estado = "EJECUTANDO"
                if i == proceso.tiempo_cpu - 1:
                    estado = "TERMINADO"
                    proceso.tiempo_fin = tiempo_actual + 1

                tabla_ejecucion[tiempo_actual] = {
                    'proceso': proceso,
                    'estado': estado,
                    'tiempo_restante': proceso.tiempo_cpu - i - 1
                }
                tiempo_actual += 1

            proceso.tiempo_espera = proceso.tiempo_inicio - proceso.tiempo_llegada

        return ResultadoSimulacion(procesos_copia, tabla_ejecucion, tiempo_actual)
