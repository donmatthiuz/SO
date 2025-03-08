#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "buffer.h"

#define TAMANO_BUFFER 10  
#define PRODUCTORES 5
#define CONSUMIDORES 5
#define ESCRITURA 3  // Cantidad máxima de items que puede llegar a escribir un productor

buffer_t buffer;
pthread_mutex_t mutex;


pthread_cond_t full, empty;


void* producer(void* arg) {
    int producer_id = *((int*)arg);
    int count = 0;

    while (count<ESCRITURA) {  
        slot_t item = {count + 1};  

        pthread_mutex_lock(&mutex);  

        while (buffer.size == buffer.capacity) { 
            pthread_cond_wait(&empty, &mutex);




        }

        buffer_insert(&buffer, &item); 
        printf("Productor %d: %d\n", producer_id, item.value);




        buffer_dump(&buffer);  

        pthread_cond_signal(&full);
        pthread_mutex_unlock(&mutex);

        count++; 
    }

    pthread_exit(NULL);
}


void* consumer(void* arg) {
    int consumer_id = *((int*)arg);
    int count = 0;
    
    while (count<ESCRITURA) { 
        slot_t item;

        pthread_mutex_lock(&mutex);

        while (buffer.size == 0) { 
            pthread_cond_wait(&full, &mutex);
        }

        buffer_remove(&buffer, &item); 



        printf("Consumidor %d: %d\n", consumer_id, item.value);
        buffer_dump(&buffer);  

        pthread_cond_signal(&empty); 
        pthread_mutex_unlock(&mutex); 

        count++;  
    }

    pthread_exit(NULL);
}

int main() {
    pthread_t producerThreads[PRODUCTORES], consumerThreads[CONSUMIDORES];
    int producer_ids[PRODUCTORES], consumer_ids[CONSUMIDORES];






    buffer_init(&buffer, 5);
    pthread_mutex_init(&mutex, NULL);

    pthread_cond_init(&full, NULL);
    pthread_cond_init(&empty, NULL);


    for (int i = 0; i < PRODUCTORES; i++) {
        producer_ids[i] = i + 1;
        pthread_create(&producerThreads[i], NULL, producer, &producer_ids[i]);
    }


    for (int i = 0; i < CONSUMIDORES; i++) {
        consumer_ids[i] = i + 1;

        pthread_create(&consumerThreads[i], NULL, consumer, &consumer_ids[i]);
    }


    for (int i = 0; i < PRODUCTORES; i++) {
        pthread_join(producerThreads[i], NULL);
    }


    for (int i = 0; i < CONSUMIDORES; i++) {
        pthread_join(consumerThreads[i], NULL);
    }


    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&full);
    pthread_cond_destroy(&empty);
    buffer_destroy(&buffer);

    return 0;
}
