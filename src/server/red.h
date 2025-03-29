
#ifndef RED_H
#define RED_H
typedef struct
{
    char nombre[50];
    char ip[50];
    struct lws *wsi;
    int status; // 0 = ACTIVO, 1 = OCUPADO, 2 = INACTIVO
    int activo;
    time_t ultima_actividad; 
} UsuarioRegistrado;
void send_to_unknow_client(const char *message, struct lws *wsi);


#endif
