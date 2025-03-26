#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct
{
    char *nombre;
    char *valor;
} VariableEntorno;

int cargar_variables_entorno(const char *ruta_archivo, VariableEntorno **variables)
{
    FILE *fp = fopen(ruta_archivo, "r");
    if (!fp)
    {
        perror("No se pudo abrir el archivo");
        return -1;
    }

    size_t capacidad = 10;
    size_t cantidad = 0;
    *variables = malloc(capacidad * sizeof(VariableEntorno));
    if (*variables == NULL)
    {
        perror("Error al asignar memoria");
        fclose(fp);
        return -1;
    }

    char linea[256];
    while (fgets(linea, sizeof(linea), fp))
    {

        linea[strcspn(linea, "\n")] = 0;

        char *igual = strchr(linea, '=');
        if (igual)
        {
            *igual = '\0';

            if (cantidad >= capacidad)
            {
                capacidad *= 2;
                *variables = realloc(*variables, capacidad * sizeof(VariableEntorno));
                if (*variables == NULL)
                {
                    perror("Error al reasignar memoria");
                    fclose(fp);
                    return -1;
                }
            }

            (*variables)[cantidad].nombre = strdup(linea);
            (*variables)[cantidad].valor = strdup(igual + 1);

            cantidad++;
        }
    }

    fclose(fp);
    return cantidad;
}

void liberar_variables(VariableEntorno *variables, size_t cantidad)
{
    for (size_t i = 0; i < cantidad; i++)
    {
        free(variables[i].nombre);
        free(variables[i].valor);
    }
    free(variables);
}

// int main() {
//     const char *archivo = ".env";  // Ruta del archivo .env
//     VariableEntorno *variables = NULL;

//     int cantidad = cargar_variables_entorno(archivo, &variables);
//     if (cantidad < 0) {
//         printf("Error al cargar las variables de entorno\n");
//         return 1;
//     }

//     // Mostrar las variables de entorno cargadas
//     for (int i = 0; i < cantidad; i++) {
//         printf("Variable: %s, Valor: %s\n", variables[i].nombre, variables[i].valor);
//     }

//     // Liberar la memoria utilizada por las variables
//     liberar_variables(variables, cantidad);

//     return 0;
// }
