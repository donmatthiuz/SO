#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
int main()
{
    fork();
    fork();
    fork();
    fork();
    printf("Hola soy un proceso\n");
    return 0;
}
