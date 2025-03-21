#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libwebsockets.h>

static int callback_client(struct lws *wsi, enum lws_callback_reasons reason, void *user, void *in, size_t len) {
    switch (reason) {
        case LWS_CALLBACK_CLIENT_ESTABLISHED:
            printf("Conexión establecida con el servidor\n");
            break;

        case LWS_CALLBACK_CLIENT_RECEIVE:
            printf("Respuesta del servidor: %s\n", (char *)in);
            break;

        case LWS_CALLBACK_CLIENT_WRITEABLE:
            // Enviar un mensaje al servidor
            const char *message = "Hola desde el cliente";
            lws_write(wsi, (unsigned char *)message, strlen(message), LWS_WRITE_TEXT);
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
    struct lws_context *context;
    struct lws_context_creation_info info = {0};
    struct lws *wsi;

    info.port = CONTEXT_PORT_NO_LISTEN;  // No escuchamos en el puerto (solo cliente)
    info.protocols = protocols;

    context = lws_create_context(&info);
    if (!context) {
        printf("Error creando el contexto\n");
        return -1;
    }

    printf("Cliente WebSocket intentando conectarse a ws://localhost:9000\n");

    // Información para conectar al servidor WebSocket
    struct lws_client_connect_info ccinfo = {0};
    ccinfo.context = context;
    ccinfo.address = "localhost";
    ccinfo.port = 9000;
    ccinfo.path = "/";
    ccinfo.protocol = "chat-protocol";  // Protocolo que usaremos
    ccinfo.origin = "localhost";  // Para completar el encabezado Origin

    // Intentamos conectar
    wsi = lws_client_connect_via_info(&ccinfo);
    if (!wsi) {
        printf("Error al intentar conectar al servidor\n");
        lws_context_destroy(context);
        return -1;
    }

    // Entrar en el bucle de servicio para el cliente
    while (1) {
        lws_service(context, 100);
    }

    lws_context_destroy(context);
    return 0;
}
