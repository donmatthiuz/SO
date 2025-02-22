#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>

int main(){
    clock_t inicio, fin;
    
    pid_t hijo;
    hijo = fork();
    if (hijo ==0 ){
        printf("Hola soy el hijo\n");
    }else{
        while (1)
        {
           
        }
        
    }
    return 0;
}
