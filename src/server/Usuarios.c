#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Definición de los estados de usuario
typedef enum
{
    ACTIVO,
    OCUPADO,
    INACTIVO
} EstadoUsuario;

// Definición de la estructura Usuario
typedef struct Usuario
{
    char ip[16];
    EstadoUsuario status;
    char nombre[50];
    struct Usuario *siguiente;
} Usuario;

// Funciones
Usuario *crearUsuario(const char *ip, EstadoUsuario status, const char *nombre);
void agregarUsuario(Usuario **cabeza, const char *ip, EstadoUsuario status, const char *nombre);
void eliminarUsuario(Usuario **cabeza, const char *nombre);
void actualizarUsuario(Usuario *cabeza, const char *nombre, EstadoUsuario nuevoStatus, const char *nuevaIp);
Usuario *obtenerUsuario(Usuario *cabeza, const char *nombre);
Usuario **obtenerTodosLosUsuarios(Usuario *cabeza, int *cantidad);
void imprimirUsuarios(Usuario *cabeza);
void liberarLista(Usuario *cabeza);

Usuario *crearUsuario(const char *ip, EstadoUsuario status, const char *nombre)
{
    Usuario *nuevo = (Usuario *)malloc(sizeof(*nuevo));
    if (!nuevo)
    {
        printf("Error al asignar memoria\n");
        return NULL;
    }
    strncpy(nuevo->ip, ip, 15);
    nuevo->ip[15] = '\0';
    nuevo->status = status;
    strncpy(nuevo->nombre, nombre, 49);
    nuevo->nombre[49] = '\0';
    nuevo->siguiente = NULL;
    return nuevo;
}

void agregarUsuario(Usuario **cabeza, const char *ip, EstadoUsuario status, const char *nombre)
{
    Usuario *nuevo = crearUsuario(ip, status, nombre);
    if (!nuevo)
        return;
    nuevo->siguiente = *cabeza;
    *cabeza = nuevo;
}

void eliminarUsuario(Usuario **cabeza, const char *nombre)
{
    Usuario *actual = *cabeza;
    Usuario *previo = NULL;
    while (actual && strcmp(actual->nombre, nombre) != 0)
    {
        previo = actual;
        actual = actual->siguiente;
    }
    if (!actual)
        return;
    if (!previo)
    {
        *cabeza = actual->siguiente;
    }
    else
    {
        previo->siguiente = actual->siguiente;
    }
    free(actual);
}

void actualizarUsuario(Usuario *cabeza, const char *nombre, EstadoUsuario nuevoStatus, const char *nuevaIp)
{
    Usuario *actual = cabeza;
    while (actual)
    {
        if (strcmp(actual->nombre, nombre) == 0)
        {
            actual->status = nuevoStatus;
            strncpy(actual->ip, nuevaIp, 15);
            actual->ip[15] = '\0';
            return;
        }
        actual = actual->siguiente;
    }
}

Usuario *obtenerUsuario(Usuario *cabeza, const char *nombre)
{
    Usuario *actual = cabeza;
    while (actual)
    {
        if (strcmp(actual->nombre, nombre) == 0)
        {
            return actual;
        }
        actual = actual->siguiente;
    }
    return NULL;
}

Usuario **obtenerTodosLosUsuarios(Usuario *cabeza, int *cantidad)
{
    *cantidad = 0;
    Usuario *actual = cabeza;
    while (actual)
    {
        (*cantidad)++;
        actual = actual->siguiente;
    }
    Usuario **usuarios = (Usuario **)malloc(*cantidad * sizeof(Usuario *));
    actual = cabeza;
    for (int i = 0; i < *cantidad; i++)
    {
        usuarios[i] = actual;
        actual = actual->siguiente;
    }
    return usuarios;
}

void imprimirUsuarios(Usuario *cabeza)
{
    Usuario *actual = cabeza;
    while (actual)
    {
        printf("IP: %s, Estado: %d, Nombre: %s\n", actual->ip, actual->status, actual->nombre);
        actual = actual->siguiente;
    }
}

void liberarLista(Usuario *cabeza)
{
    Usuario *actual = cabeza;
    while (actual)
    {
        Usuario *temp = actual;
        actual = actual->siguiente;
        free(temp);
    }
}
