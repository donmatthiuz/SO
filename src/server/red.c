#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libwebsockets.h>

static int callback_chat(struct lws *wsi, enum lws_callback_reasons reason, void *user, void *in, size_t len) {
    switch (reason) {
        case LWS_CALLBACK_ESTABLISHED:
            printf("Cliente conectado\n");
            break;

        case LWS_CALLBACK_RECEIVE:
            printf("Mensaje recibido: %s\n", (char *)in);

            // Mensaje de respuesta
            const char *response = "Mensaje recibido correctamente";
            size_t response_len = strlen(response);

            // lws_write necesita que el buffer tenga espacio adicional para LWS_PRE
            unsigned char *buffer = (unsigned char *)malloc(LWS_PRE + response_len);
            if (!buffer) {
                printf("Error al asignar memoria\n");
                return -1;
            }

            // Copiar la respuesta al buffer después del espacio de LWS_PRE
            memcpy(buffer + LWS_PRE, response, response_len);

            // Enviar el mensaje al cliente
            lws_write(wsi, buffer + LWS_PRE, response_len, LWS_WRITE_TEXT);

            // Liberar la memoria asignada
            free(buffer);
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
    struct lws_context *context;
    struct lws_context_creation_info info = {0};

    info.port = 9000;
    info.protocols = protocols;

    context = lws_create_context(&info);
    if (!context) {
        printf("Error creando el contexto\n");
        return -1;
    }

    printf("Servidor WebSocket corriendo en ws://localhost:9000\n");

    while (1) {
        lws_service(context, 100);
    }

    lws_context_destroy(context);
    return 0;
}
