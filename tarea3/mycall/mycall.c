#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/linkage.h>

SYSCALL_DEFINE1(mycall,int, i) {
 return i+14;
}
