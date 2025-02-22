#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>

#define SHM_NAME "/shared_memory"
#define SHM_SIZE 32

int main(int argc, char *argv[]) {


    if (argc != 3) {
        fprintf(stderr, "Uso: %s <n> <x>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int n = atoi(argv[1]);
    char x = argv[2][0];
    printf("HOla soy %c\n",x );

    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    printf("%c Memoria compartida creada  \n",x);
    if (shm_fd == -1) {
        perror("Error abriendo memoria compartida");
        exit(EXIT_FAILURE);
    }

    
    if (ftruncate(shm_fd, SHM_SIZE) == -1) {
        perror("Error ajustando tamaño de memoria compartida");
        exit(EXIT_FAILURE);
    }

    
    char *shm_ptr = mmap(0, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (shm_ptr == MAP_FAILED) {
        perror("Error en mmap");
        exit(EXIT_FAILURE);
    }

    
    if (shm_ptr[0] == '\0' || shm_ptr[0] == '-') {
        printf("%c Iniciando memoria \n",x);
        memset(shm_ptr, '-', SHM_SIZE);
    }else{
        printf("%c La memoria ya existe \n",x);
    }

    

   
    pid_t pid = fork();
    if (pid < 0) {
        perror("Error en fork");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) {  
        for (int i = 0; i < SHM_SIZE; i++) {
            if (i % n == 0) {
                shm_ptr[i] = x;
            }
        }
        exit(EXIT_SUCCESS);
    } else {  
        wait(NULL);
        printf("%c: Memoria compartida después de escribir: %s\n", x, shm_ptr);

        
        munmap(shm_ptr, SHM_SIZE);
        close(shm_fd);
    }

    return 0;
}