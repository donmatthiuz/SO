
# Proyecto 2 SO

---
## Proposito del proyecto

Con este proyecto se reforzarán los conocimientos sobre planificación de procesos, algoritmos de
scheduling, concurrencia y mecanismos de sincronización (mutex y semáforos). El objetivo es desarrollar
una aplicación visual y backend utilizando Python, que permita simular visualmente diferentes algoritmos
de planificación y escenarios de sincronización

## 📦 Estructura del Proyecto

```
SO-proyecto2/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── acciones.txt
│   ├── procesors.txt
│   └── recursos.txt
├── src/
│   ├── main.py
│   ├── gui/
│   │   ├── principal.py
│   │   ├── sinc.py
│   │   ├── table_schedule.py
│   │   ├── table_sinc.py
│   │   └── window.py
│   ├── scheduling/
│   │   ├── AlgoritmoPlanificacion.py
│   │   ├── FIFO.py
│   │   ├── Priority.py
│   │   ├── Round_Robin.py
│   │   ├── SJF.py
│   │   ├── SRT.py
│   │   └── resultados.py
│   ├── sincronization/
│   │   ├── Mutex.py
│   │   └── resultado.py
│   └── structure/
│       ├── actions.py
│       ├── process.py
│       └── resources.py
```

---

## ▶️ Cómo ejecutar el proyecto

### 1. Requisitos

Asegúrate de tener instalado Python 3.12+.

### 2. Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
source venv/bin/activate   # En Linux/Mac
venv\Scripts\activate      # En Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar el programa

```bash
python -m src.main
```

---

## 📁 Descripción de los archivos y carpetas

### Archivos principales

* `requirements.txt`: Lista las dependencias necesarias para ejecutar el proyecto.
* `main.py`: Punto de entrada de la aplicación, probablemente lanza la interfaz gráfica.

### Carpeta `data/`

Contiene archivos de entrada:

* `acciones.txt`: Probablemente define acciones para los procesos.
* `procesors.txt`: Define los procesadores disponibles.
* `recursos.txt`: Define los recursos utilizados por los procesos.

### Carpeta `gui/`

Contiene los módulos de la interfaz gráfica:

* `principal.py`: Ventana principal o controlador de GUI.
* `sinc.py`, `table_sinc.py`: Módulos relacionados con la sincronización.
* `table_schedule.py`: Módulo de visualización de planificación.
* `window.py`: Posiblemente define la estructura principal de la ventana.

### Carpeta `scheduling/`

Implementa los algoritmos de planificación:

* `FIFO.py`, `SJF.py`, `Round_Robin.py`, `SRT.py`, `Priority.py`: Algoritmos clásicos de planificación.
* `AlgoritmoPlanificacion.py`: Clase base o interfaz común.
* `resultados.py`: Maneja los resultados de la simulación.

### Carpeta `sincronization/`

Implementa mecanismos de sincronización:

* `Mutex.py`: Control de exclusión mutua.
* `resultado.py`: Resultados de sincronización.

### Carpeta `structure/`

Define las estructuras de datos:

* `actions.py`, `process.py`, `resources.py`: Modelan acciones, procesos y recursos.

---
