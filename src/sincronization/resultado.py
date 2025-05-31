class ResultadoSincronizacion:
    def __init__(self, procesos, recursos, tabla_estados, ciclos_totales):
        self.procesos = procesos
        self.recursos = recursos
        self.tabla_estados = tabla_estados
        self.ciclos_totales = ciclos_totales


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
        tiempo_total_promedio = sum(p.tiempo_fin - p.tiempo_llegada for p in procesos_terminados) / len(procesos_terminados)
        estadisticas += f"Tiempo total promedio: {tiempo_total_promedio:.2f} ciclos\n\n"
    
    estadisticas += "=== DETALLES POR PROCESO ===\n"
    for proceso in procesos:
        estadisticas += f"{proceso.pid}: "
        estadisticas += f"Llegada={proceso.tiempo_llegada}, "
        estadisticas += f"BurstTime={proceso.tiempo_cpu}, "
        estadisticas += f"Prioridad={proceso.prioridad}, "
        if proceso.tiempo_fin:
            estadisticas += f"Terminó en ciclo {proceso.tiempo_fin}, "
            estadisticas += f"Tiempo total={proceso.tiempo_fin - proceso.tiempo_llegada}\n"
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
                    detalle += f" (usando {', '.join(info['recursos_usando'])}  {info["accion_actual"]})"
                
                detalle += f" [TR: {info['tiempo_restante']}]\n"
            
            # Estado de recursos
            detalle += "  Recursos: "
            for recurso in resultado.recursos.values():
                detalle += f"{recurso.nombre}({recurso.contador_actual}/{recurso.contador_inicial}) "
            detalle += "\n\n"
    
    return detalle
