#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Definición de los estados de usuario
typedef enum {
    ACTIVO,
    OCUPADO,
    INACTIVO
} EstadoUsuario;

// Definición de la estructura Usuario
typedef struct Usuario {
    char ip[16]; 
    EstadoUsuario status; 
    char nombre[50]; 
    struct Usuario* siguiente; 
} Usuario;

// Funciones
Usuario* crearUsuario(const char* ip, EstadoUsuario status, const char* nombre);
void agregarUsuario(Usuario** cabeza, const char* ip, EstadoUsuario status, const char* nombre);
void eliminarUsuario(Usuario** cabeza, const char* nombre);
void actualizarUsuario(Usuario* cabeza, const char* nombre, EstadoUsuario nuevoStatus, const char* nuevaIp);
Usuario* obtenerUsuario(Usuario* cabeza, const char* nombre);
Usuario** obtenerTodosLosUsuarios(Usuario* cabeza, int* cantidad);
void imprimirUsuarios(Usuario* cabeza);
void liberarLista(Usuario* cabeza);


Usuario* crearUsuario(const char* ip, EstadoUsuario status, const char* nombre) {
    Usuario* nuevo = (Usuario*)malloc(sizeof(*nuevo));
    if (!nuevo) {
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

void agregarUsuario(Usuario** cabeza, const char* ip, EstadoUsuario status, const char* nombre) {
    Usuario* nuevo = crearUsuario(ip, status, nombre);
    if (!nuevo) return;
    nuevo->siguiente = *cabeza;
    *cabeza = nuevo;
}

void eliminarUsuario(Usuario** cabeza, const char* nombre) {
    Usuario* actual = *cabeza;
    Usuario* previo = NULL;
    while (actual && strcmp(actual->nombre, nombre) != 0) {
        previo = actual;
        actual = actual->siguiente;
    }
    if (!actual) return;
    if (!previo) {
        *cabeza = actual->siguiente;
    } else {
        previo->siguiente = actual->siguiente;
    }
    free(actual);
}

void actualizarUsuario(Usuario* cabeza, const char* nombre, EstadoUsuario nuevoStatus, const char* nuevaIp) {
    Usuario* actual = cabeza;
    while (actual) {
        if (strcmp(actual->nombre, nombre) == 0) {
            actual->status = nuevoStatus;
            strncpy(actual->ip, nuevaIp, 15);
            actual->ip[15] = '\0';
            return;
        }
        actual = actual->siguiente;
    }
}

Usuario* obtenerUsuario(Usuario* cabeza, const char* nombre) {
    Usuario* actual = cabeza;
    while (actual) {
        if (strcmp(actual->nombre, nombre) == 0) {
            return actual;
        }
        actual = actual->siguiente;
    }
    return NULL;
}

Usuario** obtenerTodosLosUsuarios(Usuario* cabeza, int* cantidad) {
    *cantidad = 0;
    Usuario* actual = cabeza;
    while (actual) {
        (*cantidad)++;
        actual = actual->siguiente;
    }
    Usuario** usuarios = (Usuario**)malloc(*cantidad * sizeof(Usuario*));
    actual = cabeza;
    for (int i = 0; i < *cantidad; i++) {
        usuarios[i] = actual;
        actual = actual->siguiente;
    }
    return usuarios;
}

void imprimirUsuarios(Usuario* cabeza) {
    Usuario* actual = cabeza;
    while (actual) {
        printf("IP: %s, Estado: %d, Nombre: %s\n", actual->ip, actual->status, actual->nombre);
        actual = actual->siguiente;
    }
}

void liberarLista(Usuario* cabeza) {
    Usuario* actual = cabeza;
    while (actual) {
        Usuario* temp = actual;
        actual = actual->siguiente;
        free(temp);
    }
}

// int main() {
//     Usuario* listaUsuarios = NULL;
    
//     agregarUsuario(&listaUsuarios, "192.168.1.1", ACTIVO, "Alice");
//     agregarUsuario(&listaUsuarios, "192.168.1.2", OCUPADO, "Bob");
//     agregarUsuario(&listaUsuarios, "192.168.1.3", INACTIVO, "Charlie");
    
//     imprimirUsuarios(listaUsuarios);
    
//     printf("\nActualizando usuario Bob...\n");
//     actualizarUsuario(listaUsuarios, "Bob", ACTIVO, "192.168.1.4");
//     imprimirUsuarios(listaUsuarios);
    
//     printf("\nEliminando usuario Alice...\n");
//     eliminarUsuario(&listaUsuarios, "Alice");
//     imprimirUsuarios(listaUsuarios);
    
//     Usuario* buscado = obtenerUsuario(listaUsuarios, "Charlie");
//     if (buscado) {
//         printf("\nUsuario encontrado: IP: %s, Estado: %d, Nombre: %s\n", buscado->ip, buscado->status, buscado->nombre);
//     }
    
//     printf("\nObteniendo todos los usuarios...\n");
//     int cantidad;
//     Usuario** usuarios = obtenerTodosLosUsuarios(listaUsuarios, &cantidad);
//     for (int i = 0; i < cantidad; i++) {
//         printf("Usuario %d -> IP: %s, Estado: %d, Nombre: %s\n", i + 1, usuarios[i]->ip, usuarios[i]->status, usuarios[i]->nombre);
//     }
//     free(usuarios);
    
//     printf("\nLiberando lista de usuarios...\n");
//     liberarLista(listaUsuarios);
    
//     return 0;
// }