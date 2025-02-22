#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>

#define SHM_NAME "/shared_memory"

int main() {
    pid_t pid1, pid2;

   
    if ((pid1 = fork()) == 0) {
        execl("./ipc", "ipc", "3", "B", NULL);
        perror("Error ejecutando ipc");
        exit(EXIT_FAILURE);
    }
    wait(NULL);  


    if ((pid2 = fork()) == 0) {
        execl("./ipc", "ipc", "5", "A", NULL);
        perror("Error ejecutando ipc");
        exit(EXIT_FAILURE);
    }
    wait(NULL);

    // Eliminar memoria compartida después de la ejecución
    if (shm_unlink(SHM_NAME) == 0) {
        printf("Memoria compartida eliminada correctamente.\n");
    } else {
        perror("Error eliminando memoria compartida");
    }

    return 0;
}