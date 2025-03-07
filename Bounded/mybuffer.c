/*

Este no es mi implementacion de buffer la saque de esta otra implementacion del buffer
link : https://github.com/oscarp-info/linux-thread-in-C/blob/main/20_prod_cons/parte_2/buffer.c


*/



#include "buffer.h"

int buffer_init(buffer_t * buffer, int capacity){
    
    buffer->array = malloc(capacity*sizeof(slot_t));
    
    

    buffer->capacity = capacity;
    buffer->size = 0;
    buffer->head = 0;
    buffer->tail = 0;

    return EXIT_SUCCESS;

}

int buffer_insert(buffer_t* buffer, slot_t *slot){
    if ( buffer->size < buffer->capacity){
        buffer->array[buffer->head] = *slot;
        buffer->head = (buffer->head +1 )%buffer->capacity;
        buffer->size++;
        return EXIT_SUCCESS;
    }
    return EXIT_FAILURE;
}

int buffer_remove(buffer_t* buffer, slot_t * slot){
    if (buffer->size >0){
        *slot = buffer->array[buffer->tail];
        buffer->tail = (buffer->tail +1 )%buffer->capacity;
        buffer->size--;
        return EXIT_SUCCESS;
    }
    return EXIT_FAILURE;
}

void buffer_destroy(buffer_t * buffer){
    free(buffer->array);

}

void buffer_dump(buffer_t* buffer){
    int i,j;
    
    fprintf(stderr, "\n---- El buffer ---\n");
    fprintf(stderr, "tamano: %d\n", buffer->size);
    fprintf(stderr, "cabeza: %d\n", buffer->head);
    fprintf(stderr, "cola: %d\n", buffer->tail);
    fprintf(stderr, "\n");

    j = buffer->tail;
    for(i=0; i< buffer->size; i++){
        fprintf(stderr, "buffer[%d]: (%d)\n", j, buffer->array[j].value);
        j = (j+1)%buffer->capacity;
    }
    fprintf(stderr, "--------------------------\n");

}