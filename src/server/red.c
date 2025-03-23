#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libwebsockets.h>

static int callback_chat(struct lws *wsi, enum lws_callback_reasons reason, void *user, void *in, size_t len) {
    switch (reason) {
        case LWS_CALLBACK_ESTABLISHED:
            printf("Cliente conectado: Protocolo WebSocket activado\n");
            break;

        case LWS_CALLBACK_RECEIVE:
            char *message = malloc(len + 1);
            if (!message) {
                printf("Error al asignar memoria\n");
                return -1;
            } 
            
            // Copiar exactamente 'len' bytes del mensaje recibido
            memcpy(message, in, len);
            message[len] = '\0'; // Agregar el terminador nulo
            
            printf("Mensaje recibido (longitud %zu): %s\n", len, message);
            
            // Resto del código para responder...
            
            free(message);
            break;

        case LWS_CALLBACK_CLOSED:
            printf("Cliente desconectado\n");
            break;

        default:
            break;
    }
    return 0;
}

static struct lws_protocols protocols[] = {
    { "chat-protocol", callback_chat, 0, 4096 },
    { NULL, NULL, 0, 0 }
};

int main() {
    struct lws_context_creation_info info = {0};
    struct lws_context *context;

    info.port = 5000;
    info.protocols = protocols;
    info.gid = -1;
    info.uid = -1;

    context = lws_create_context(&info);
    if (!context) {
        printf("Error creando el contexto WebSocket\n");
        return -1;
    }

    printf("Servidor WebSocket corriendo en ws://localhost.com:9000/chat\n");

    while (1) {
        lws_service(context, 100);
    }

    lws_context_destroy(context);
    return 0;
}
