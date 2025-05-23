class Process:
    def __init__(self, pid: str, burstTime: int, arrivalTime: int, priority: int):
        self.pid = pid
        self.burst_time = burstTime
        self.arrival_time = arrivalTime
        self.remaining_time = burstTime
        self.priority = priority
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.is_completed = False

def cargar_procesos_desde_archivo(ruta: str):
    procesos = []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue  # Saltar líneas vacías

                partes = [p.strip() for p in linea.split(",")]
                if len(partes) >= 4:
                    p = Process(
                        pid=partes[0],
                        burstTime=int(partes[1]),
                        arrivalTime=int(partes[2]),
                        priority=int(partes[3])
                    )
                    procesos.append(p)
                else:
                    print(f"Formato incorrecto en línea: {linea}")
    except FileNotFoundError:
        print(f"No se pudo abrir el archivo: {ruta}")
    return procesos

