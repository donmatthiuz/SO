#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libwebsockets.h>

static int callback_client(struct lws *wsi, enum lws_callback_reasons reason, void *user, void *in, size_t len) {
    switch (reason) {
        case LWS_CALLBACK_CLIENT_ESTABLISHED:
            printf("Conexión establecida con el servidor WebSocket\n");

            // Enviar mensaje al servidor
            const char *message = "Hola desde el cliente!";
            size_t message_len = strlen(message);

            unsigned char *buffer = (unsigned char *)malloc(LWS_PRE + message_len);
            if (!buffer) {
                printf("Error al asignar memoria\n");
                return -1;
            }

            memcpy(buffer + LWS_PRE, message, message_len);
            lws_write(wsi, buffer + LWS_PRE, message_len, LWS_WRITE_TEXT);

            free(buffer);
            break;

        case LWS_CALLBACK_CLIENT_RECEIVE:
            printf("Respuesta del servidor: %s\n", (char *)in);
            break;

        case LWS_CALLBACK_CLOSED:
            printf("Conexión cerrada\n");
            break;

        default:
            break;
    }
    return 0;
}

static struct lws_protocols protocols[] = {
    { "chat-protocol", callback_client, 0, 4096 },
    { NULL, NULL, 0, 0 }
};

int main() {
    struct lws_context_creation_info info = {0};
    struct lws_context *context;
    struct lws *wsi;

    info.port = CONTEXT_PORT_NO_LISTEN;
    info.protocols = protocols;

    context = lws_create_context(&info);
    if (!context) {
        printf("Error creando el contexto WebSocket\n");
        return -1;
    }

    printf("Cliente WebSocket intentando conectarse a ws://chatservidor.example.com:9000/chat\n");

    struct lws_client_connect_info ccinfo = {0};
    ccinfo.context = context;
    ccinfo.address = "localhost";
    ccinfo.port = 5000;
    ccinfo.path = "/";
    ccinfo.protocol = "chat-protocol";
    ccinfo.origin = "34.201.114.218";

    wsi = lws_client_connect_via_info(&ccinfo);
    if (!wsi) {
        printf("Error al intentar conectar al servidor\n");
        lws_context_destroy(context);
        return -1;
    }

    while (1) {
        lws_service(context, 100);
    }

    lws_context_destroy(context);
    return 0;
}
