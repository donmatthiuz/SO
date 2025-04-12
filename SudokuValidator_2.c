#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdbool.h>  // Incluye la librería para usar bool
#include <pthread.h>  // Para trabajar con hilos (threads)
#include <sys/syscall.h>
#include <sys/wait.h>
#include <omp.h>      // Agregamos la librería OpenMP


#define SUDOKU_SIZE 9
#define SHARED_MEMORY_NAME "/sudoku_matriz"

int (*sudoku_matriz)[SUDOKU_SIZE];  // Esta es la matriz de 9 x 9

void imprimir_sudoku() {
  printf("Sudoku leído:\n");
  for (int i = 0; i < SUDOKU_SIZE; i++) {
      for (int j = 0; j < SUDOKU_SIZE; j++) {
          printf("%d ", sudoku_matriz[i][j]);
      }
      printf("\n");
  }
}


bool verificar_fila(int fila) {
    bool numero_visto[10] = { false }; 

    for (int j = 0; j < 9; j++) {
        int num = sudoku_matriz[fila][j];
        if (num >= 1 && num <= 9) {
            if (numero_visto[num]) {
                printf("Número repetido %d en la fila %d, columna %d\n", num, fila, j);
                return false;
            }
            numero_visto[num] = true;
        } else {
            printf("Número inválido %d en la fila %d, columna %d\n", num, fila, j);
            return false;
        }
    }

    
    for (int k = 1; k <= 9; k++) {
        if (!numero_visto[k]) {
            printf("Falta el número %d en la fila %d\n", k, fila);
            return false;
        }
    }

    return true;
}



bool verificar_columna(int columna) {
    bool numero_visto[10] = { false }; 

    for (int i = 0; i < 9; i++) {
        int num = sudoku_matriz[i][columna];
        if (num >= 1 && num <= 9) {
            if (numero_visto[num]) {
                printf("Número repetido %d en la columna %d, fila %d\n", num, columna, i);
                return false;
            }
            numero_visto[num] = true;
        } else {
            printf("Número inválido %d en la columna %d, fila %d\n", num, columna, i);
            return false;
        }
    }

    for (int k = 1; k <= 9; k++) {
        if (!numero_visto[k]) {
            printf("Falta el número %d en la columna %d\n", k, columna);
            return false;
        }
    }

    return true;
}

bool verificar_subarreglo_3x3(int fila_inicio, int columna_inicio) {
    bool numero_visto[10] = { false }; 

    for (int i = fila_inicio; i < fila_inicio + 3; i++) {
        for (int j = columna_inicio; j < columna_inicio + 3; j++) {
            int num = sudoku_matriz[i][j];
            if (num >= 1 && num <= 9) {
                if (numero_visto[num]) {
                    printf("Número repetido %d en el bloque que inicia en fila %d, columna %d\n", num, fila_inicio, columna_inicio);
                    return false;
                }
                numero_visto[num] = true;
            } else {
                printf("Número inválido %d en el bloque que inicia en fila %d, columna %d (posición interna fila %d, columna %d)\n", num, fila_inicio, columna_inicio, i, j);
                return false;
            }
        }
    }

    for (int k = 1; k <= 9; k++) {
        if (!numero_visto[k]) {
            printf("Falta el número %d en el bloque que inicia en fila %d, columna %d\n", k, fila_inicio, columna_inicio);
            return false;
        }
    }

    return true;
}


bool revisar_todas_filas(){
    bool resultado = true;
    
    #pragma omp parallel for private(resultado)
    for (int i = 0; i < SUDOKU_SIZE; i++) {
        if (!verificar_fila(i)) {
            #pragma omp critical
            {
                printf("El sudoku es invalido en la fila %d\n", i);
                resultado = false;
            }
        }
    }
    
    return resultado;
}

bool revisar_todas_columnas(void *arg){
    pid_t id_del_hilo = syscall(SYS_gettid);
    printf("El thread que ejecuta el método para ejecutar la revisión de columnas es: %d\n", id_del_hilo);
    
    bool resultado = true;
    
    #pragma omp parallel for private(id_del_hilo)
    for (int i = 0; i < SUDOKU_SIZE; i++){
        id_del_hilo = syscall(SYS_gettid);
        if(!verificar_columna(i)){
            #pragma omp critical
            {
                printf("El sudoku es invalido en la columna %d\n", i);
                resultado = false;
            }
        }
        printf("En la revision de columnas el siguiente es un thread en ejecucion: %d\n", id_del_hilo);
    }
    
    pthread_exit(NULL);
}

void ejecutar_ps_thread(long hilo_del_padre){
    char string_del_hilo[20];
    snprintf(string_del_hilo, sizeof(string_del_hilo), "%ld", hilo_del_padre);

    execlp("ps", "ps", "-p", string_del_hilo, "-lLf", (char *)NULL);

    perror("execlp falló");
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s archivo_sudoku.txt\n", argv[0]);
        return 1;
    }

    
    int shm_fd = shm_open(SHARED_MEMORY_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("Error al crear memoria compartida");
        return 1;
    }

    
    if (ftruncate(shm_fd, sizeof(int) * SUDOKU_SIZE * SUDOKU_SIZE) == -1) {
        perror("Error al definir tamaño de memoria compartida");
        close(shm_fd);
        return 1;
    }

    sudoku_matriz = mmap(NULL, sizeof(int) * SUDOKU_SIZE * 
                SUDOKU_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (sudoku_matriz == MAP_FAILED) {
        perror("Error al mapear memoria compartida");
        close(shm_fd);
        return 1;
    }

    close(shm_fd);

   
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

    
    int index = 0;
    for (int i = 0; i < SUDOKU_SIZE; i++) {
        for (int j = 0; j < SUDOKU_SIZE; j++) {
            sudoku_matriz[i][j] = buffer[index++] - '0';
        }
    }

    pid_t padre = getpid();
    pid_t hijo = fork();

    if (hijo == 0) {
        pthread_t thread;
        pthread_create(&thread, NULL, revisar_todas_columnas, NULL);
        pthread_join(thread, NULL);
        ejecutar_ps_thread((long)padre);
    }

    waitpid(hijo, NULL, 0);
    bool valido = true;
    
    #pragma omp parallel for shared(valido)
    for (int i = 0; i < SUDOKU_SIZE; i++) {
        if (!verificar_fila(i)) {
            #pragma omp critical
            {
                printf("Sudoku inválido en fila %d\n", i);
                valido = false;
            }
        }
    }
    
    if (valido)
        printf("Sudoku válido.\n");
    else
        printf("Sudoku inválido.\n");
        
    pid_t hijo2 = fork();
    if (hijo2 == 0) {
        printf("Antes de terminar el estado de este proceso y sus threads es: \n");
        ejecutar_ps_thread((long)padre);
    }

    waitpid(hijo2, NULL, 0);

    bool subarreglos_validos = true;
    
    #pragma omp parallel for collapse(2) shared(subarreglos_validos)
    for (int i = 0; i < SUDOKU_SIZE; i += 3) {
        for (int j = 0; j < SUDOKU_SIZE; j += 3) {
            if (!verificar_subarreglo_3x3(i, j)) {
                #pragma omp critical
                {
                    printf("El sudoku es invalido en el subarreglo que inicia en fila %d, columna %d\n", i, j);
                    subarreglos_validos = false;
                }
            }
        }
    }

    if (!subarreglos_validos) {
        printf("El sudoku es invalido\n");
        return EXIT_FAILURE;
    }

    
    imprimir_sudoku();

   
    munmap(sudoku_matriz, sizeof(int) * SUDOKU_SIZE * SUDOKU_SIZE);
    shm_unlink(SHARED_MEMORY_NAME);

    return 0;
}