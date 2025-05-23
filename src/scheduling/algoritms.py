from collections import deque

def fifo(procesos):
    orden = procesos[:] 
    n = len(orden)

    for i in range(n):
        for j in range(0, n - 1 - i):
            if orden[j].arrivalTime > orden[j + 1].arrivalTime:
              
                orden[j], orden[j + 1] = orden[j + 1], orden[j]

    return orden

def round_robin(procesos_original, quantum):
    procesos = sorted(procesos_original, key=lambda p: p.arrivalTime)
    resultado = []
    cola = deque()
    tiempo = 0
    i = 0

    bt_restantes = {p.pid: p.burstTime for p in procesos}

    while i < len(procesos) or cola:
        while i < len(procesos) and procesos[i].arrivalTime <= tiempo:
            cola.append(procesos[i])
            i += 1

        if not cola:
            tiempo += 1
            continue

        actual = cola.popleft()
        restante = bt_restantes[actual.pid]
        ejecutar = min(restante, quantum)


        bt_restantes[actual.pid] -= ejecutar
        tiempo += ejecutar

        resultado.append(actual)

        while i < len(procesos) and procesos[i].arrivalTime <= tiempo:
            cola.append(procesos[i])
            i += 1

        if bt_restantes[actual.pid] > 0:
            cola.append(actual)

    return resultado

def calcular_tiempo_espera_promedio(procesos_original, ejecucion):
    arrival_map = {p.pid: p.arrivalTime for p in procesos_original}
    primera_ejecucion = {}
    tiempo = 0

    for p in ejecucion:
        if p.pid not in primera_ejecucion:
            primera_ejecucion[p.pid] = tiempo
        tiempo += 1

    total_espera = 0.0
    for pid, inicio in primera_ejecucion.items():
        total_espera += inicio - arrival_map[pid]

    return total_espera / len(procesos_original)
