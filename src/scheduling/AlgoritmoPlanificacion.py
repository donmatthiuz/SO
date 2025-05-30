from abc import ABC, abstractmethod

class AlgoritmoPlanificacion(ABC):
    def __init__(self, **kwargs):
        self.procesos = kwargs.get('procesos', [])

    @abstractmethod
    def simular(self):
        pass
