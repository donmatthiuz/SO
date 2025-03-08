#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>

int clientes_count = 0;
sem_t mutex;
sem_t acceso_cocina;

void *cliente(void *arg) {
    int cliente_id = *(int*)arg;
    
    while (1) {
        sleep(1);
        
        sem_wait(&mutex);
        clientes_count++;
        if (clientes_count == 1) {
            sem_wait(&acceso_cocina);
        }
        sem_post(&mutex);
        
        printf("Cliente %d está consultando el menú. Clientes activos: %d\n", cliente_id, clientes_count);
        sleep(2);  
        
        sem_wait(&mutex);
        clientes_count--;
        if (clientes_count == 0) {
            sem_post(&acceso_cocina);
        }
        sem_post(&mutex);
        
        printf("Cliente %d terminó de consultar el menú\n", cliente_id);
    }
    return NULL;
}

void *chef(void *arg) {
    int chef_id = *(int*)arg;
    
    while (1) {
        sleep(3);
        
        printf("Chef %d está intentando actualizar el menú\n", chef_id);
        sem_wait(&acceso_cocina);
        
        printf("Chef %d está actualizando el menú\n", chef_id);
        sleep(2);  
        
        sem_post(&acceso_cocina);
        printf("Chef %d terminó de actualizar el menú\n", chef_id);
    }
    return NULL;
}

int main() {
    srand(time(NULL));
    
    // Inicializa los semáforos:
    // mutex se usa para proteger el contador de clientes
    sem_init(&mutex, 0, 1);
    // acceso_cocina garantiza acceso exclusivo a la cocina (para chefs)
    sem_init(&acceso_cocina, 0, 1);
    
    // Crea hilos para clientes y chefs
    pthread_t clientes[5], chefs[2];
    int ids[5];
    
    // Asigna IDs a los clientes (y para los chefs se reutilizan los dos primeros IDs)
    for (int i = 0; i < 5; i++) {
        ids[i] = i + 1;
    }
    
    // Crea hilos para clientes
    for (int i = 0; i < 5; i++) {
        pthread_create(&clientes[i], NULL, cliente, &ids[i]);
    }
    
    // Crea hilos para chefs
    for (int i = 0; i < 2; i++) {
        pthread_create(&chefs[i], NULL, chef, &ids[i]);
    }
    
    // Espera a los hilos (el programa se ejecuta indefinidamente)
    for (int i = 0; i < 5; i++) {
        pthread_join(clientes[i], NULL);
    }
    for (int i = 0; i < 2; i++) {
        pthread_join(chefs[i], NULL);
    }
    
    // Destruye los semáforos
    sem_destroy(&mutex);
    sem_destroy(&acceso_cocina);
    
    return 0;
}
