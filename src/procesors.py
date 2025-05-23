class Procesors:
    def __init__(self, pid: str, burstTime: int, arrivalTime: int, priority: int):
        self.pid = pid
        self.burstTime = burstTime
        self.arrivalTime = arrivalTime
        self.priority = priority
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
                    p = Procesors(
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

