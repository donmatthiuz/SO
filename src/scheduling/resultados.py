class ResultadoSimulacion:
    def __init__(self, procesos, tabla_ejecucion, tiempo_total):
        self.procesos = procesos  # Lista de procesos originales
        self.tabla_ejecucion = tabla_ejecucion  # Diccionario con la ejecución por tiempo
        self.tiempo_total = tiempo_total
        
    def get_proceso_en_tiempo(self, tiempo):
        """Retorna el proceso que se ejecuta en un tiempo dado"""
        return self.tabla_ejecucion.get(tiempo, None)
    

def generar_estadisticas(resultado):
    """Genera estadísticas de la simulación"""
    procesos = resultado.procesos
    tiempo_total = resultado.tiempo_total
    
    if not procesos:
        return "No hay procesos para mostrar estadísticas."
    
    tiempo_espera_total = sum(p.tiempo_espera for p in procesos if p.tiempo_espera is not None)
    tiempo_respuesta_total = sum(p.tiempo_respuesta for p in procesos if p.tiempo_respuesta is not None)
    
    promedio_espera = tiempo_espera_total / len(procesos)
    promedio_respuesta = tiempo_respuesta_total / len(procesos)
    
    estadisticas = f"=== ESTADÍSTICAS ===\n"
    estadisticas += f"Tiempo total de simulación: {tiempo_total}\n"
    estadisticas += f"Tiempo de espera promedio: {promedio_espera:.2f}\n"
    estadisticas += f"Tiempo de respuesta promedio: {promedio_respuesta:.2f}\n\n"
    
    estadisticas += "=== DETALLES POR PROCESO ===\n"
    for proceso in procesos:
        estadisticas += f"{proceso.pid}: "
        estadisticas += f"Llegada={proceso.tiempo_llegada}, "
        estadisticas += f"CPU={proceso.tiempo_cpu}, "
        estadisticas += f"Inicio={proceso.tiempo_inicio}, "
        estadisticas += f"Fin={proceso.tiempo_fin}, "
        estadisticas += f"Espera={proceso.tiempo_espera}, "
        estadisticas += f"Respuesta={proceso.tiempo_respuesta}\n"
    
    return estadisticas
