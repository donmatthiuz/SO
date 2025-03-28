#include <stdio.h>
#include <stdlib.h>
#include <string.h>



const char *color_info = "\033[1;36m";
const char *color_wait = "\033[1;33m";
const char *color_user_input = "\033[1;32m";
const char *color_error = "\033[1;31m";

const char *color_labels = "\033[1;36m";        // celeste
const char *color_message = "\033[1;37m";       // blanco
const char *color_private_label = "\033[1;35m"; // rosa
const char *color_other_user = "\033[1;33m";    // amarillo
const char *color_my_user = "\033[1;32m";       // verde
const char *color_desconection = "\033[1;31m";  // rojo
const char *color_input = "\033[1;30m";         // gris
const char *color_reset = "\033[0m";

const char *color_border = "\033[1;34m"; // Azul brillante





void seleccionar_estado(char *estado, char *status_global) {
  int opcion;
  printf("%sSelecciona tu estado:%s\n", color_info, color_reset);
  printf("1. ACTIVO\n");
  printf("2. OCUPADO\n");
  printf("3. INACTIVO\n");
  printf("> ");
  scanf("%d", &opcion);
  getchar(); // Capturar el salto de línea

  switch (opcion) {
      case 1:
          strcpy(estado, "ACTIVO");
          strcpy(status_global, "ACTIVO");
          break;
      case 2:
          strcpy(estado, "OCUPADO");
          strcpy(status_global, "OCUPADO");
          break;
      case 3:
          strcpy(estado, "INACTIVO");
          strcpy(status_global, "INACTIVO");
          break;
      default:
          printf("%sOpción no válida, manteniendo estado actual.%s\n", color_info, color_reset);
          break;
  }
}


void mostrar_comandos() {
  printf("%s+---------------------------------------------------------------+%s\n", color_border, color_reset);
  printf("%s|                         Comandos Disponibles                  |%s\n", color_info, color_reset);
  printf("%s+---------------------------------------------------------------+%s\n", color_border, color_reset);
  printf("%s| /registrar <nombre_usuario>                                   |%s\n", color_labels, color_reset);
  printf("%s|   Te registras al chat con nombre de usuario                 .|%s\n", color_wait, color_reset);

  printf("%s| /broadcast <mensaje>                                          |%s\n", color_labels, color_reset);
  printf("%s|   Envía un mensaje a todos los usuarios conectados en el chat.|%s\n", color_message, color_reset);
  printf("%s|   Ejemplo: /broadcast Hola, ¿cómo están todos?                |%s\n", color_wait, color_reset);

  printf("%s| /private <usuario> <mensaje>                                  |%s\n", color_labels, color_reset);
  printf("%s|   Envía un mensaje privado a un usuario específico.           |%s\n", color_message, color_reset);
  printf("%s|   Ejemplo: /private juan Hola, ¿puedes ayudarme?              |%s\n", color_wait, color_reset);

  printf("%s| /list                                                         |%s\n", color_labels, color_reset);
  printf("%s|   Muestra la lista de usuarios conectados en el chat.         |%s\n", color_message, color_reset);
  printf("%s|   Ejemplo: /list                                              |%s\n", color_wait, color_reset);

  printf("%s| /info <usuario>                                               |%s\n", color_labels, color_reset);
  printf("%s|   Muestra información sobre un usuario específico.            |%s\n", color_message, color_reset);
  printf("%s|   Ejemplo: /info juan                                         |%s\n", color_wait, color_reset);

  printf("%s| /status <estado>                                              |%s\n", color_labels, color_reset);
  printf("%s|   Cambia tu estado (por ejemplo: en línea, ocupado, ausente). |%s\n", color_message, color_reset);
  printf("%s|   Ejemplo: /status ocupado                                    |%s\n", color_wait, color_reset);
  
  printf("%s| /ayuda                                                        |%s\n", color_labels, color_reset);
  printf("%s|  Mostrar los comandos que puedo usar                          |%s\n", color_message, color_reset);
  printf("%s|   Ejemplo: /ayuda                                             |%s\n", color_wait, color_reset);

  printf("%s| /exit                                                         |%s\n", color_labels, color_reset);
  printf("%s|   Cierra la conexión y sale del chat.                         |%s\n", color_message, color_reset);
  printf("%s|   Ejemplo: /exit                                              |%s\n", color_wait, color_reset);

  printf("%s+---------------------------------------------------------------+%s\n", color_border, color_reset);

  printf("\n%sRecuerda que puedes escribir cualquier mensaje para enviarlo al chat público, si no usas un comando específico. ¡Diviértete!%s\n", color_wait, color_reset);
}