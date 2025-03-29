# Proyecto Chat Sistemas Operativos

## Protocolo

[Click aqui](doc/protocolo.md)

## Cliente Funcionamiento

[Click aqui](doc/cliente.md)

## Servidor

[Click aqui](doc/servidor.md)

## Instalaciones

Para ejecutar el programa sigue los siguientes pasos

- Instale las librerias

cjson

```bash
sudo apt update
sudo apt install libcjson-dev
```

pthreads

```bash
sudo apt install libpthread-stubs0-dev
```

libwebsockets

```bash
sudo apt install libwebsockets-dev
```

- Server: Luego vayase a la carpeta src y server:

```bash
gcc cliente.c parser.c ui.c -o cliente.o -lwebsockets -lpthread -lcjson
```

- Cambie el .env de src/cliente

```bash
SERVER=IP DE SU SERVER
PUERTO=PUERTO DEL SERVER
```

- Cliente: Luego vayase a la carpeta src/cliente y ejecute:

```bash
gcc red.c parser.c -o server.o -lwebsockets -lpthread -lcjson
```

## Descripcion

### Proyecto de Chat en C con Sockets

### **Descripción**

Este proyecto consiste en la implementación de un sistema de chat en C utilizando sockets y multithreading para la comunicación entre clientes y un servidor. Se basa en un modelo desarrollado en 2006 por Bob Dugan y Erik Véliz y está diseñado para reforzar conocimientos sobre concurrencia, procesos y comunicación entre procesos en sistemas operativos.

### **Componentes del Proyecto**

#### **Servidor**

- Mantiene una lista de usuarios conectados.
- Solo puede haber una instancia en ejecución.
- Atiende múltiples clientes usando hilos (multithreading).
- Registra usuarios, maneja estados, lista usuarios y permite envío de mensajes.
- Se ejecuta con el siguiente comando:

  ```bash
  <nombredelservidor> <puertodelservidor>
  ```

  Donde:
  - `<nombredelservidor>` es el nombre del programa.
  - `<puertodelservidor>` es el puerto en el que escucha conexiones.

#### **Cliente**

- Se conecta al servidor y se registra con un nombre único.
- Puede enviar y recibir mensajes en un chat general o privado.
- Puede cambiar su estado (ACTIVO, OCUPADO, INACTIVO).
- Puede solicitar información sobre otros usuarios.
- Se ejecuta con el siguiente comando:

  ```bash
  <nombredelcliente> <nombredeusuario> <IPdelservidor> <puertodelservidor>
  ```

  Donde:
  - `<nombredelcliente>` es el nombre del programa.
  - `<nombredeusuario>` es el identificador del cliente en el chat.
  - `<IPdelservidor>` y `<puertodelservidor>` son los datos del servidor.

### **Funciones del Servidor**

- **Registro de usuarios:** Guarda el usuario y su IP, rechazando duplicados.
- **Manejo de desconexión:** Elimina de la lista a usuarios que cierran sesión.
- **Listar usuarios:** Responde con la lista de usuarios conectados.
- **Obtener información de usuario:** Devuelve la IP de un usuario específico.
- **Cambio de estado:** Los usuarios pueden cambiar entre ACTIVO, OCUPADO e INACTIVO.
- **Mensajería:** Permite el chat general (broadcast) y mensajes directos.

### **Funciones del Cliente**

El cliente debe permitir:

1. Chatear con todos los usuarios (broadcasting).
2. Enviar y recibir mensajes directos.
3. Cambiar de estado.
4. Listar usuarios conectados.
5. Obtener información de un usuario en particular.
6. Acceder a ayuda.
7. Salir del sistema.

El formato para enviar mensajes será:

```bash
<usuario> <mensaje>
```

Donde:

- `<usuario>` es el destinatario.
- `<mensaje>` es el texto a enviar.
