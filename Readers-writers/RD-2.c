#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>


int clientes_contando = 0;     
int chefs_en_espera = 0;       
sem_t mutex;                   
sem_t acceso_carta;            
sem_t acceso_cocina;           
sem_t mutex_chefs;             

void *cliente(void *arg) {
    int cliente_id = *(int*)arg;
    
    while (1) {
        sleep(rand() % 3 + 1);
        
        printf("Cliente %d está esperando para consultar la carta\n", cliente_id);
        
        sem_wait(&acceso_carta);     
        sem_wait(&mutex);            
        
        clientes_contando++;
        if (clientes_contando == 1) {
            sem_wait(&acceso_cocina);
        }
        
        sem_post(&mutex);            
        sem_post(&acceso_carta);     
        
        printf("Cliente %d está consultando la carta. Clientes actuales: %d\n", cliente_id, clientes_contando);
        sleep(2);  
        
        sem_wait(&mutex);            
        
        clientes_contando--;
        if (clientes_contando == 0) {
            sem_post(&acceso_cocina);
        }
        
        sem_post(&mutex);            
        printf("Cliente %d ha terminado de consultar la carta\n", cliente_id);
    }
    
    return NULL;
}


void *chef(void *arg) {
    int chef_id = *(int*)arg;
    
    while (1) {
        sleep(rand() % 5 + 1);
        
        sem_wait(&mutex_chefs);
        chefs_en_espera++;
        if (chefs_en_espera == 1) {
            sem_wait(&acceso_carta);
        }
        sem_post(&mutex_chefs);
        
        printf("Chef %d está esperando para actualizar el menú del día\n", chef_id);
        sem_wait(&acceso_cocina);    
        
        printf("Chef %d está actualizando el menú del día\n", chef_id);
        sleep(2);  
        
        sem_post(&acceso_cocina);
        
        sem_wait(&mutex_chefs);
        chefs_en_espera--;
        if (chefs_en_espera == 0) {
            sem_post(&acceso_carta);
        }
        sem_post(&mutex_chefs);
        
        printf("Chef %d ha terminado de actualizar el menú\n", chef_id);
    }
    
    return NULL;
}

int main() {
    srand(time(NULL));
    
    // Inicializa semáforos
    sem_init(&mutex, 0, 1);
    sem_init(&acceso_carta, 0, 1);
    sem_init(&acceso_cocina, 0, 1);
    sem_init(&mutex_chefs, 0, 1);
    
    // Crea hilos para clientes y chefs
    pthread_t clientes[5], chefs[3];
    int ids[5];
    
    // Inicialización de IDs
    for (int i = 0; i < 5; i++) {
        ids[i] = i + 1;
    }
    
    // Crea hilos de clientes (lectores)
    for (int i = 0; i < 5; i++) {
        pthread_create(&clientes[i], NULL, cliente, &ids[i]);
    }
    
    for (int i = 0; i < 3; i++) {
        pthread_create(&chefs[i], NULL, chef, &ids[i]);
    }
    
    for (int i = 0; i < 5; i++) {
        pthread_join(clientes[i], NULL);
    }
    for (int i = 0; i < 3; i++) {
        pthread_join(chefs[i], NULL);
    }
    
    // Destruye semáforos
    sem_destroy(&mutex);
    sem_destroy(&acceso_carta);
    sem_destroy(&acceso_cocina);
    sem_destroy(&mutex_chefs);
    
    return 0;
}