#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>


int main(){
    pid_t hijo, nieto, bisnieto;
    clock_t inicio, fin;

    inicio = clock();

    hijo = fork();

    if (hijo == 0){
        nieto = fork();

        if (nieto == 0){
            bisnieto = fork();

            if (bisnieto ==0){
                for (int i=0; i<1000000 ;i++){
                    printf("Indice %d\n", i);
                }
                printf("Proceso bisnieto\n");
            }else{
                wait(NULL);
                printf("Proceso nieto\n");
                for (int i=0; i<1000000 ;i++){
                    printf("Indice %d\n", i);
                }
            }
        }else{
            wait(NULL);
            printf("Proceso hijo\n");
            for (int i=0; i<1000000 ;i++){
                printf("Indice %d\n", i);
            }
        }
    }else{
        wait(NULL);
        printf("Proceso papa\n");
        fin = clock();
        double ejecucion_;
        ejecucion_ = ((double) fin - inicio) / CLOCKS_PER_SEC;
    
        printf("Ejecucion en %f\n", ejecucion_);
    }

}
