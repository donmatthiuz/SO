#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

#define SUDOKU_SIZE 9
#define SHARED_MEMORY_NAME "/sudoku_matriz"

int (*sudoku_matriz)[SUDOKU_SIZE];  // Esta es la matriz de 9 x 9

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s archivo_sudoku.txt\n", argv[0]);
        return 1;
    }

    // creamos la memmoria
    int shm_fd = shm_open(SHARED_MEMORY_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("Error al crear memoria compartida");
        return 1;
    }

    // aqui le asignamos
    if (ftruncate(shm_fd, sizeof(int) * SUDOKU_SIZE * SUDOKU_SIZE) == -1) {
        perror("Error al definir tamaño de memoria compartida");
        close(shm_fd);
        return 1;
    }

    sudoku_matriz = mmap(NULL, sizeof(int) * SUDOKU_SIZE * SUDOKU_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (sudoku_matriz == MAP_FAILED) {
        perror("Error al mapear memoria compartida");
        close(shm_fd);
        return 1;
    }

    close(shm_fd);

    // Abrir y leer el archivo de Sudoku
    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror("Error al abrir el archivo");
        return 1;
    }

    char buffer[SUDOKU_SIZE * SUDOKU_SIZE + 1];
    if (fgets(buffer, sizeof(buffer), file) == NULL) {
        perror("Error al leer el archivo");
        fclose(file);
        return 1;
    }
    fclose(file);


    // relleno de la matriz
    int index = 0;
    for (int i = 0; i < SUDOKU_SIZE; i++) {
        for (int j = 0; j < SUDOKU_SIZE; j++) {
            sudoku_matriz[i][j] = buffer[index++] - '0';
        }
    }

    
    printf("Sudoku leído:\n");
    for (int i = 0; i < SUDOKU_SIZE; i++) {
        for (int j = 0; j < SUDOKU_SIZE; j++) {
            printf("%d ", sudoku_matriz[i][j]);
        }
        printf("\n");
    }

    // eliminar memoria compartida
    munmap(sudoku_matriz, sizeof(int) * SUDOKU_SIZE * SUDOKU_SIZE);
    shm_unlink(SHARED_MEMORY_NAME);

    return 0;
}
