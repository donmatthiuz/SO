#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
int main()
{
    for (int i=0; i<4;i++){
        fork();
        printf("va por el for %d ", i);
        printf("Hola soy un proceso en un for\n");

    }
    return 0;
}
