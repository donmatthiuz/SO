#include <stdio.h>
#include <stdlib.h>

char* crearJson(const char* nombre, const char* valor) {
    // Calcular el tamaño del string resultante
    int tamaño = snprintf(NULL, 0, "{\"nombre\": \"%s\", \"valor\": \"%s\"}", nombre, valor) + 1;

    // Asignar memoria para el string resultante
    char* resultado = (char*)malloc(tamaño);
    if (!resultado) {
        printf("Error al asignar memoria\n");
        return NULL;
    }

    // Crear el JSON con snprintf
    snprintf(resultado, tamaño, "{\"nombre\": \"%s\", \"valor\": \"%s\"}", nombre, valor);

    return resultado;
}

// int main() {
//     const char* nombre = "ejemplo";
//     const char* valor = "123";

//     // Crear el string JSON
//     char* json = crearJson(nombre, valor);

//     // Imprimir el resultado
//     if (json) {
//         printf("%s\n", json);
//         free(json);  // Liberar la memoria
//     }

//     return 0;
// }
