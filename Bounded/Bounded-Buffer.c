#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "buffer.h"

#define MAX_ITEMS 10  

buffer_t buffer;
pthread_mutex_t mutex;
pthread_cond_t full, empty;

void* producer(void* arg) {
    for (int i = 0; i < MAX_ITEMS; i++) {
        slot_t item = {i + 1};

        pthread_mutex_lock(&mutex);
        while (buffer.size == buffer.capacity) {
            pthread_cond_wait(&empty, &mutex);
        }

        buffer_insert(&buffer, &item);
        printf("Productor: %d\n", item.value);
        buffer_dump(&buffer);

        pthread_cond_signal(&full);
        pthread_mutex_unlock(&mutex);
    }
    pthread_exit(NULL);
}

void* consumer(void* arg) {
    for (int i = 0; i < MAX_ITEMS; i++) {
        slot_t item;

        pthread_mutex_lock(&mutex);
        while (buffer.size == 0) { 
            pthread_cond_wait(&full, &mutex);
        }

        buffer_remove(&buffer, &item);
        printf("Consumidor: %d\n", item.value);
        buffer_dump(&buffer);

        pthread_cond_signal(&empty);
        pthread_mutex_unlock(&mutex);
    }
    pthread_exit(NULL);
}

int main() {
    pthread_t producerThread, consumerThread;

    buffer_init(&buffer, 5); 
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
