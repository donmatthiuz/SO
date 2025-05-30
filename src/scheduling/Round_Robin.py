import copy
from src.scheduling.resultados import ResultadoSimulacion
from src.scheduling.AlgoritmoPlanificacion import AlgoritmoPlanificacion


class RoundRobin(AlgoritmoPlanificacion):
    def __init__(self, quantum, **kwargs):
        super().__init__(**kwargs)
        self.quantum = quantum

    def simular(self):
        procesos_copia = copy.deepcopy(self.procesos)
        procesos_copia.sort(key=lambda p: p.tiempo_llegada)
        
        cola = []
        tabla_ejecucion = {}
        tiempo_actual = 0
        i = 0
        
        while i < len(procesos_copia) and procesos_copia[i].tiempo_llegada <= tiempo_actual:
            cola.append(procesos_copia[i])
            i += 1

        while cola or i < len(procesos_copia):
            if not cola:
                if i < len(procesos_copia):
                    tiempo_actual = procesos_copia[i].tiempo_llegada
                    cola.append(procesos_copia[i])
                    i += 1
                continue

            proceso_actual = cola.pop(0)

            if proceso_actual.tiempo_inicio is None:
                proceso_actual.tiempo_inicio = tiempo_actual
                proceso_actual.tiempo_respuesta = tiempo_actual - proceso_actual.tiempo_llegada

            tiempo_ejecucion = min(self.quantum, proceso_actual.tiempo_restante)

            for _ in range(tiempo_ejecucion):
                estado = "EJECUTANDO"
                proceso_actual.tiempo_restante -= 1

                if proceso_actual.tiempo_restante == 0:
                    estado = "TERMINADO"
                    proceso_actual.tiempo_fin = tiempo_actual + 1

                tabla_ejecucion[tiempo_actual] = {
                    'proceso': proceso_actual,
                    'estado': estado,
                    'tiempo_restante': proceso_actual.tiempo_restante
                }
                tiempo_actual += 1

            while i < len(procesos_copia) and procesos_copia[i].tiempo_llegada <= tiempo_actual:
                cola.append(procesos_copia[i])
                i += 1

            if proceso_actual.tiempo_restante > 0:
                cola.append(proceso_actual)

        for proceso in procesos_copia:
            if proceso.tiempo_inicio is not None and proceso.tiempo_fin is not None:
                tiempo_total = proceso.tiempo_fin - proceso.tiempo_llegada
                proceso.tiempo_espera = tiempo_total - proceso.tiempo_cpu

        return ResultadoSimulacion(procesos_copia, tabla_ejecucion, tiempo_actual)
