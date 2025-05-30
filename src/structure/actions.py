class Accion:
    def __init__(self, pid, accion, recurso, ciclo):
        self.pid = pid
        self.accion = accion.upper()  # READ, WRITE
        self.recurso = recurso
        self.ciclo = ciclo
        self.ejecutada = False
        self.ciclo_inicio = None
        self.ciclo_fin = None
    
    def __str__(self):
        return f"Accion({self.pid}, {self.accion}, {self.recurso}, ciclo:{self.ciclo})"

def cargar_acciones_desde_archivo(archivo):
    """Carga acciones desde un archivo de texto con formato: <PID>, <ACCION>, <RECURSO>, <CICLO>"""
    acciones = []
    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith('#'):
                    partes = [p.strip() for p in linea.split(',')]
                    if len(partes) >= 4:
                        pid = partes[0]
                        accion = partes[1].lower()  # convierte a minúsculas
                        recurso = partes[2]
                        ciclo = int(partes[3])
                        acciones.append(Accion(pid, accion, recurso, ciclo))
    except FileNotFoundError:
        print(f"Archivo no encontrado: {archivo}")
    except Exception as e:
        print(f"Error cargando acciones: {e}")
    
    return acciones