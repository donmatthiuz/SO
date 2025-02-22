#include <stdio.h>
#include <time.h>


int main(){
    clock_t inicio, fin;
    
    inicio = clock();
    for (int i=0; i<1000000 ;i++){
        printf("Indice %d\n", i);
    };
    for (int i=0; i<1000000 ;i++){
        printf("Indice %d\n", i);
    }
    for (int i=0; i<1000000 ;i++){
        printf("Indice %d\n", i);
    }
    fin = clock();

    double ejecucion_;
    ejecucion_ = ((double) fin - inicio) / CLOCKS_PER_SEC;

    printf("Ejecucion en %f\n", ejecucion_);

    return 0;
}