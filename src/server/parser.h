#include "red.h"
#ifndef PARSER_H
#define PARSER_H

typedef struct
{
  char key[50];
  char value[50];
  int isNumber;
} JsonPair;

void remove_spaces(char *str);
void extract_json(const char *input, char *output);
int parse_json(const char *json_str, JsonPair *pairs, int max_pairs);
const char *getValueByKey(JsonPair *pares, int cantidad, const char *clave);

// Funciones para crear mensajes JSON
char *crearJson_register(const char *nombre_usuario);
char *crearJson_broadcast(const char *sender, const char *mensaje);
char *crearJson_private(const char *sender, const char *target, const char *mensaje);
char *crearJson_list_users(const char *sender);
char *crearJson_user_info(const char *sender, const char *target);
char *crearJson_change_status(const char *sender, const char *nuevo_estado);
char *crearJson_disconnect(const char *sender);
char *crearJson_Registro_Exitoso(const char *sender, const char *tiempo, UsuarioRegistrado *usuarios, int max_usuarios);
char *crearjsonError(const char *sender,const char *tiempo, const char *contenido);
char *crearJson_Brodcast_register(const char *sender, const char *tiempo, const char* nombre_usuario);
char *crearJsonCambi_status_server(const char *sender,const char *tiempo, const char *contenido);

#endif
