#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libwebsockets.h>

static int callback_client(struct lws *wsi, enum lws_callback_reasons reason, void *user, void *in, size_t len) {
    switch (reason) {
        case LWS_CALLBACK_CLIENT_ESTABLISHED:
            printf("Conexión establecida con el servidor\n");

            // Enviar mensaje de bienvenida al servidor una vez que la conexión esté establecida
            const char *message = "Hola desde el cliente!";
            size_t message_len = strlen(message);

            // Necesitamos espacio adicional para LWS_PRE
            unsigned char *buffer = (unsigned char *)malloc(LWS_PRE + message_len);
            if (!buffer) {
                printf("Error al asignar memoria\n");
                return -1;
            }

            // Copiar el mensaje en el buffer, después del espacio LWS_PRE
            memcpy(buffer + LWS_PRE, message, message_len);

            // Enviar el mensaje al servidor
            lws_write(wsi, buffer + LWS_PRE, message_len, LWS_WRITE_TEXT);

            // Liberar la memoria asignada
            free(buffer);
            break;

        case LWS_CALLBACK_CLIENT_RECEIVE:
            // Recibir la respuesta del servidor
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
    struct lws_context *context;
    struct lws_context_creation_info info = {0};
    struct lws *wsi;

    info.port = CONTEXT_PORT_NO_LISTEN;  // El cliente no necesita escuchar, solo se conecta
    info.protocols = protocols;

    // Crear el contexto de WebSocket
    context = lws_create_context(&info);
    if (!context) {
        printf("Error creando el contexto\n");
        return -1;
    }

    printf("Cliente WebSocket intentando conectarse a ws://localhost:9000\n");

    // Información de conexión al servidor WebSocket
    struct lws_client_connect_info ccinfo = {0};
    ccinfo.context = context;
    ccinfo.address = "localhost";   // Dirección del servidor
    ccinfo.port = 9000;             // Puerto del servidor
    ccinfo.path = "/";              // Ruta de la conexión
    ccinfo.protocol = "chat-protocol";  // El protocolo usado
    ccinfo.origin = "localhost";    // El origen (opcional, generalmente el mismo)

    // Intentar conectar al servidor
    wsi = lws_client_connect_via_info(&ccinfo);
    if (!wsi) {
        printf("Error al intentar conectar al servidor\n");
        lws_context_destroy(context);
        return -1;
    }

    // Ejecutar el bucle de eventos de WebSocket para recibir y enviar mensajes
    while (1) {
        lws_service(context, 100);
    }

    // Limpiar el contexto después de la ejecución
    lws_context_destroy(context);
    return 0;
}
