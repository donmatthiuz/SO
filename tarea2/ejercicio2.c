#include <stdio.h>
#include <unistd.h>


int main(int argc, char* argv[]) {
    // Verificar si se han pasado argumentos
    if (argc < 2) {
        printf("No se han pasado argumentos.\n");
    } else {
        printf("Se han pasado %d argumento(s):\n", argc - 1); // Restamos 1 por el nombre del programa
        for (int i = 1; i < argc; i++) {
            printf("Argumento %d: %s\n", i, argv[1]);
        }
    }
    return 0;
}
