/*
ABBY SOFIA DONIS AGREDA - 22440
5 filosofos y 5 tenedores
- cada filosofo necesita 2 tenedores para comer
- se deben usar Mutex y/o semaforos
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

pthread_t filosofo[5];
pthread_mutex_t tenedor[5];

//proceso filosofos
void *func(void *arg){
    int iFilosofo = *(int *)arg;
    free (arg);
    printf("\n Filosofo %d piensa 🧎", iFilosofo);
    sleep(1);
    //tomar tenedores
    if (iFilosofo == 4){
        pthread_mutex_lock(&tenedor[(iFilosofo + 1) %5]);
        pthread_mutex_lock(&tenedor[iFilosofo]);
    } else {
        pthread_mutex_lock(&tenedor[iFilosofo]);
        pthread_mutex_lock(&tenedor[(iFilosofo + 1) %5]);
    }
    printf("\n Filosofo %d toma tenedores %d y %d", iFilosofo, iFilosofo, (iFilosofo+1)%5);
    printf("\n Filosofo %d come 🥄(-o-)🥄", iFilosofo);
    sleep(1);
    //dejar tenedores
    pthread_mutex_unlock(&tenedor[iFilosofo]);
    pthread_mutex_unlock(&tenedor[(iFilosofo+1)%5]);
    printf("\n Filosofo %d termina de comer y deja tenedores %d y %d (-w-)", iFilosofo, iFilosofo, (iFilosofo+1)%5);

    return NULL;
}

//iniciar problema 
int main(){
    int i, j;
    for(i = 0; i <= 4; i++){
        j = pthread_mutex_init(&tenedor[i], NULL);
        if (j != 0){
            printf("\n Error al iniciar mutex");
            exit(1);
        }
    }
    for( i = 0; i<=4; i++){
        int *iFilosofo = malloc(sizeof(int));
        *iFilosofo = i;
        j =  pthread_create(&filosofo[i], NULL, func, iFilosofo);
        if (j != 0){
            printf("\n Error al iniciar thread");
            exit(1);
        }
    }
    // terminar a final de hilo
    for( i = 0; i<=4; i++){
        j = pthread_join(filosofo[i], NULL);
        if (j != 0){
            printf("\n Error al esperar finalizacion de thread");
            exit(1);
        }
    }
    //tenedores dispobiles
    for( i = 0; i<=4; i++){
        j = pthread_mutex_destroy(&tenedor[i]);
        if (j != 0){
            printf("\n Error al desbloquear tenedores");
            exit(1);
        }
    }
    return 0;
}