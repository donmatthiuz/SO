#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#define MAXBUFLEN 1000

int main(int argc, char* argv[]) {
   
   

   
    int fd = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC);
    if (fd == -1) {
        perror("No se pudo abrir el archivo de salida");
        return 1;
    }

 
    FILE *fp = fopen(argv[1], "r");
    if (fp != NULL) {
        char buffer[MAXBUFLEN];
        size_t bytesRead;
        
 
        while ((bytesRead = fread(buffer, sizeof(char), MAXBUFLEN, fp)) > 0) {
            // Escribir el contenido leído en el archivo de salida
            ssize_t bytesWritten = write(fd, buffer, bytesRead);
            if (bytesWritten == -1) {
                perror("Error al escribir en el archivo");
                close(fd);
                fclose(fp);
                return 1;
            }
        }

        // Cerrar los archivos
        fclose(fp);
        close(fd);
    } else {
        perror("No se pudo abrir el archivo de entrada");
        close(fd);
        return 1;
    }

    return 0;
}
