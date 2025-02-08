#include <unistd.h>
#include <stdio.h>
#include <sys/syscall.h>


int main(){
  int x = syscall(468,15);
  printf("%d\n",x);
  return 0;


}
