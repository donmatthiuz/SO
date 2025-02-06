#include <stdio.h>
#include <unistd.h>


int main(){
  

  int f = fork();

  if(f==0){
      execl("./ejercicio1","./ejercicio1",(char *)NULL);
    }else{
      printf("ID_1: %d\n", (int)getpid());
      execl("./ejercicio1","./ejercicio1",(char *)NULL);
      
    }
  return (0);
}