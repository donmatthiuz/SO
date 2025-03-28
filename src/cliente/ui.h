#ifndef CHAT_COMMANDS_H
#define CHAT_COMMANDS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Definición de colores para la consola
extern const char *color_info;
extern const char *color_wait;
extern const char *color_user_input;
extern const char *color_error;
extern const char *color_labels;
extern const char *color_message;
extern const char *color_private_label;
extern const char *color_other_user;
extern const char *color_my_user;
extern const char *color_desconection;
extern const char *color_input;
extern const char *color_reset;
extern const char *color_border;

// Funciones
void seleccionar_estado(char *estado, char *status_global);
void mostrar_comandos();

#endif // CHAT_COMMANDS_H