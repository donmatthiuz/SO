#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *nombre;
    char *valor;
} VariableEntorno;

int cargar_variables_entorno(const char *ruta_archivo, VariableEntorno **variables) {
    FILE *fp = fopen(ruta_archivo, "r");
    if (!fp) {
        perror("No se pudo abrir el archivo");
        return -1; // Error al abrir el archivo
    }

    size_t capacidad = 10; // Número inicial de variables
    size_t cantidad = 0;   // Número actual de variables
    *variables = malloc(capacidad * sizeof(VariableEntorno));
    if (*variables == NULL) {
        perror("Error al asignar memoria");
        fclose(fp);
        return -1;
    }

    char linea[256];
    while (fgets(linea, sizeof(linea), fp)) {
        // Eliminar salto de línea
        linea[strcspn(linea, "\n")] = 0;

        // Buscar el signo "="
        char *igual = strchr(linea, '=');
        if (igual) {
            *igual = '\0';  // Cortar la cadena en el '='

            // Asegurarse de que hay espacio suficiente en el arreglo de variables
            if (cantidad >= capacidad) {
                capacidad *= 2;
                *variables = realloc(*variables, capacidad * sizeof(VariableEntorno));
                if (*variables == NULL) {
                    perror("Error al reasignar memoria");
                    fclose(fp);
                    return -1;
                }
            }

            // Asignar el nombre y el valor de la variable de entorno
            (*variables)[cantidad].nombre = strdup(linea);  // Copia el nombre de la variable
            (*variables)[cantidad].valor = strdup(igual + 1); // Copia el valor de la variable

            cantidad++;
        }
    }

    fclose(fp);
    return cantidad;  // Devuelve la cantidad de variables cargadas
}

void liberar_variables(VariableEntorno *variables, size_t cantidad) {
    for (size_t i = 0; i < cantidad; i++) {
        free(variables[i].nombre);
        free(variables[i].valor);
    }
    free(variables);
}

int main() {
    const char *archivo = ".env";  // Ruta del archivo .env
    VariableEntorno *variables = NULL;

    int cantidad = cargar_variables_entorno(archivo, &variables);
    if (cantidad < 0) {
        printf("Error al cargar las variables de entorno\n");
        return 1;
    }

    // Mostrar las variables de entorno cargadas
    for (int i = 0; i < cantidad; i++) {
        printf("Variable: %s, Valor: %s\n", variables[i].nombre, variables[i].valor);
    }

    // Liberar la memoria utilizada por las variables
    liberar_variables(variables, cantidad);

    return 0;
}
