class Recurso:
    def __init__(self, nombre, contador):
        self.nombre = nombre
        self.contador_inicial = contador
        self.contador_actual = contador
        self.procesos_usando = []  
        self.cola_espera = []      
    
    def esta_disponible(self):
        return self.contador_actual > 0
    
    def set_contador(self,contador):
        self.contador_actual = contador
        self.contador_inicial = contador
    
    def asignar_a_proceso(self, proceso):
        if self.esta_disponible():
            self.contador_actual -= 1
            self.procesos_usando.append(proceso)
            return True
        else:
            if proceso not in self.cola_espera:
                self.cola_espera.append(proceso)
            return False
    
    def liberar_de_proceso(self, proceso):
        if proceso in self.procesos_usando:
            self.procesos_usando.remove(proceso)
            self.contador_actual += 1
            
            
            if self.cola_espera and self.esta_disponible():
                siguiente_proceso = self.cola_espera.pop(0)
                self.asignar_a_proceso(siguiente_proceso)
                return siguiente_proceso
        return None
    
    def __str__(self):
        return f"Recurso({self.nombre}, {self.contador_actual}/{self.contador_inicial})"

def cargar_recursos_desde_archivo(archivo):
    """Carga recursos desde un archivo de texto con formato: <NOMBRE>, <CONTADOR>"""
    recursos = {}
    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith('#'):
                    partes = [p.strip() for p in linea.split(',')]
                    if len(partes) == 2:
                        nombre = partes[0]
                        try:
                            contador = int(partes[1])
                            recursos[nombre] = Recurso(nombre, contador)
                        except ValueError:
                            print(f"Contador inválido para el recurso '{nombre}': {partes[1]}")
    except FileNotFoundError:
        print(f"Archivo no encontrado: {archivo}. Se usarán recursos por defecto.")
        recursos = {
            "R1": Recurso("R1", 1),
            "R2": Recurso("R2", 1),
        }
    except Exception as e:
        print(f"Error cargando recursos: {e}")
    
    return recursos
