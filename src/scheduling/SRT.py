import copy
from src.scheduling.resultados import ResultadoSimulacion
from src.scheduling.AlgoritmoPlanificacion import AlgoritmoPlanificacion

class SRTF(AlgoritmoPlanificacion):
    def simular(self):
        procesos_copia = copy.deepcopy(self.procesos)
        tiempo_actual = 0
        completados = 0
        tabla_ejecucion = {}
        procesos_en_espera = set()
        
        for p in procesos_copia:
            p.tiempo_restante = p.tiempo_cpu
            p.tiempo_inicio = None

        while completados < len(procesos_copia):
           
            listos = [
                p for p in procesos_copia 
                if p.tiempo_llegada <= tiempo_actual and p.tiempo_restante > 0
            ]

            if listos:
                
                actual = min(listos, key=lambda p: p.tiempo_restante)

                
                if actual.tiempo_inicio is None:
                    actual.tiempo_inicio = tiempo_actual
                    actual.tiempo_respuesta = tiempo_actual - actual.tiempo_llegada

                
                actual.tiempo_restante -= 1

                estado = "EJECUTANDO"
                if actual.tiempo_restante == 0:
                    estado = "TERMINADO"
                    actual.tiempo_fin = tiempo_actual + 1
                    completados += 1
                    actual.tiempo_espera = (
                        actual.tiempo_fin - actual.tiempo_llegada - actual.tiempo_cpu
                    )

                tabla_ejecucion[tiempo_actual] = {
                    'proceso': actual,
                    'estado': estado,
                    'tiempo_restante': actual.tiempo_restante
                }

                tiempo_actual += 1
            else:
                
                tiempo_actual += 1

        return ResultadoSimulacion(procesos_copia, tabla_ejecucion, tiempo_actual)
