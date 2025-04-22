#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/list.h>


static int __init simple_init(void){
    printk(KERN_INFO "Loading Module\nEstoy en el sistema operativo");
    return 0;
}


static void __exit simple_exit(void){
    printk(KERN_INFO "Removing Module\nEstoy afuera en el sistema operativo");
}

module_init(simple_init);
module_exit(simple_exit);
MODULE_LICENSE("GPL");

MODULE_DESCRIPTION("Practica de Cargar y Descargar.");
MODULE_AUTHOR("MATHEW CORDERO AQUINO - 22982");