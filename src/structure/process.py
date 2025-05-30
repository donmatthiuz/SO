class Proceso:
    def __init__(self, pid, tiempo_llegada, tiempo_cpu, prioridad=0):
        self.pid = pid
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_cpu = tiempo_cpu
        self.prioridad = prioridad
        self.tiempo_restante = tiempo_cpu
        self.tiempo_inicio = None
        self.tiempo_fin = None
        self.tiempo_espera = 0
        self.tiempo_respuesta = None
    
    def __str__(self):
        return f"Proceso({self.pid}, TA:{self.tiempo_llegada}, CPU:{self.tiempo_cpu})"

def cargar_procesos_desde_archivo(archivo):
    procesos = []
    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                print("Línea leída:", linea)
                if linea and not linea.startswith('#'):
                    partes = linea.split(',')
                    if len(partes) >= 3:
                        pid = partes[0].strip()
                        tiempo_cpu = int(partes[1].strip())
                        tiempo_llegada = int(partes[2].strip())
                        prioridad = int(partes[3].strip()) if len(partes) > 3 else 0
                        proceso = Proceso(pid, tiempo_llegada, tiempo_cpu, prioridad)
                        procesos.append(proceso)
    except FileNotFoundError:
        print("Archivo no encontrado, usando valores por defecto.")
        procesos = [
            Proceso("A", 0, 3, 1),
            Proceso("B", 2, 6, 2),
            Proceso("C", 4, 4, 3),
            Proceso("D", 8, 2, 4),
        ]
    except Exception as e:
        print(f"Error cargando procesos: {e}")
    
    # Imprimir los procesos cargados
    print("Procesos cargados:")
    for p in procesos:
        print(f"PID: {p.pid}, Llegada: {p.tiempo_llegada}, CPU: {p.tiempo_cpu}, Prioridad: {p.prioridad}")
    
    return procesos
