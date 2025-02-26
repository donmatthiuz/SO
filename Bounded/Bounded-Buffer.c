#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "buffer.h"

#define MAX_ITEMS 10  // Número total de elementos a producir/consumir

buffer_t buffer;
pthread_mutex_t mutex;
pthread_cond_t full, empty;

void* producer(void* arg) {
    for (int i = 0; i < MAX_ITEMS; i++) {
        slot_t item = {i + 1}; // Crear elemento

        pthread_mutex_lock(&mutex);
        while (buffer.size == buffer.capacity) {  // Espera si el buffer está lleno
            pthread_cond_wait(&empty, &mutex);
        }

        buffer_insert(&buffer, &item);
        printf("Produced: %d\n", item.value);

        pthread_cond_signal(&full); // Notifica que hay elementos para consumir
        pthread_mutex_unlock(&mutex);
    }
    pthread_exit(NULL);
}

void* consumer(void* arg) {
    for (int i = 0; i < MAX_ITEMS; i++) {
        slot_t item;

        pthread_mutex_lock(&mutex);
        while (buffer.size == 0) {  // Espera si el buffer está vacío
            pthread_cond_wait(&full, &mutex);
        }

        buffer_remove(&buffer, &item);
        printf("Consumed: %d\n", item.value);

        pthread_cond_signal(&empty); // Notifica que hay espacio disponible
        pthread_mutex_unlock(&mutex);
    }
    pthread_exit(NULL);
}

int main() {
    pthread_t producerThread, consumerThread;

    buffer_init(&buffer, 5); // Crear buffer de tamaño 5
    pthread_mutex_init(&mutex, NULL);
    pthread_cond_init(&full, NULL);
    pthread_cond_init(&empty, NULL);

    pthread_create(&producerThread, NULL, producer, NULL);
    pthread_create(&consumerThread, NULL, consumer, NULL);

    pthread_join(producerThread, NULL);
    pthread_join(consumerThread, NULL);

    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&full);
    pthread_cond_destroy(&empty);
    buffer_destroy(&buffer);

    return 0;
}
