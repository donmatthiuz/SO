#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <libwebsockets.h>
#include "getENV.c"
#include "parser.c"
#include <pthread.h>
#include <signal.h>

static int connection_open = 0; // 1 si está conectado, 0 si no

char* get_local_ip() {
    char hostbuffer[256];
    struct hostent *host_entry;
    int hostname;

    hostname = gethostname(hostbuffer, sizeof(hostbuffer));
    if (hostname == -1) {
        perror("gethostname failed");
        return NULL;
    }

    host_entry = gethostbyname(hostbuffer);
    if (host_entry == NULL) {
        perror("gethostbyname failed");
        return NULL;
    }

    struct in_addr *address = (struct in_addr*) host_entry->h_addr_list[0];
    return inet_ntoa(*address);
}

static int callback_client(struct lws *wsi, enum lws_callback_reasons reason, void *user, void *in, size_t len) {
    switch (reason) {
        case LWS_CALLBACK_CLIENT_ESTABLISHED:
            printf("Conexión establecida con el servidor WebSocket\n");
            connection_open = 1; // Marcar que la conexión está abierta
            break;

        case  LWS_CALLBACK_CLIENT_RECEIVE:
            // Mostrar mensaje recibido
            printf("\nMensaje recibido: %s\n", (char *)in);
            printf("> ");
            fflush(stdout);  // Asegurarse de que el prompt se imprima de nuevo
            break;

        case LWS_CALLBACK_CLOSED:
            printf("Conexión cerrada\n");
            connection_open = 0; // Marcar que la conexión ha sido cerrada
            break;

        case LWS_CALLBACK_CLIENT_CONNECTION_ERROR:
            printf("Error de conexión: %s\n", (char *)in);
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

void* leer_mensajes(void *arg) {
    struct lws *wsi = (struct lws*) arg;
    char user_input[256];

    while (connection_open) {
        printf("> ");
        if (fgets(user_input, sizeof(user_input), stdin)) {
            user_input[strcspn(user_input, "\n")] = 0;  // Eliminar el salto de línea al final

            // Crear JSON para el mensaje
            char* json = crearJson_register(user_input);
            if (json && strlen(json) > 0) {
                unsigned char *buffer = (unsigned char *)calloc(1, LWS_PRE + strlen(json));
                if (!buffer) {
                    printf("Error al asignar memoria\n");
                    return NULL;
                }

                // Copiar el JSON al buffer WebSocket
                memcpy(buffer + LWS_PRE, json, strlen(json));

                // Enviar el mensaje al servidor WebSocket
                lws_write(wsi, buffer + LWS_PRE, strlen(json), LWS_WRITE_TEXT);

                free(buffer);
                free(json); 
            }
        }
    }
    return NULL;
}

int main() {
    // obtenemos la ip del servidor
    const char *archivo = ".env";
    VariableEntorno *variables = NULL;
    int cantidad = cargar_variables_entorno(archivo, &variables);
    if (cantidad < 0) {
        printf("Error al cargar las variables de entorno\n");
        return 1;
    }

    struct lws_context_creation_info info = {0};
    struct lws_context *context;
    struct lws *wsi;

    // Obtener la IP local
    char *local_ip = get_local_ip();
    if (local_ip == NULL) {
        printf("No se pudo obtener la IP local\n");
        return -1;
    }

    info.port = CONTEXT_PORT_NO_LISTEN;
    info.protocols = protocols;

    context = lws_create_context(&info);
    if (!context) {
        printf("Error creando el contexto WebSocket\n");
        return -1;
    }

    printf("Cliente WebSocket intentando conectarse a ws://%s:9000/chat\n", local_ip);

    struct lws_client_connect_info ccinfo = {0};
    ccinfo.context = context;
    ccinfo.address = variables[0].valor; // Dirección del servidor
    ccinfo.port = atoi(variables[1].valor);
    ccinfo.path = "/";
    ccinfo.protocol = "chat-protocol";
    ccinfo.origin = local_ip; // Asignar la IP local al campo origin

    wsi = lws_client_connect_via_info(&ccinfo);
    if (!wsi) {
        printf("Error al intentar conectar al servidor\n");
        lws_context_destroy(context);
        return -1;
    }

    // Esperar hasta que la conexión se haya establecido
    while (!connection_open) {
        lws_service(context, 100);
        printf("Esperando a que la conexión se establezca...\n");
        usleep(100000);  // Esperar un poco antes de seguir
    }

    // Solo pedir el usuario una vez
    char user_input[256];
    printf("Escribe tu usuario: ");
    if (fgets(user_input, sizeof(user_input), stdin)) {
        user_input[strcspn(user_input, "\n")] = 0;  // Eliminar el salto de línea al final
    }

    // Crear JSON para el usuario registrado
    char* json = crearJson_register(user_input);
    if (json && strlen(json) > 0) {
        unsigned char *buffer = (unsigned char *)calloc(1, LWS_PRE + strlen(json));
        if (!buffer) {
            printf("Error al asignar memoria\n");
            return -1;
        }

        // Copiar el JSON al buffer WebSocket
        memcpy(buffer + LWS_PRE, json, strlen(json));

        // Enviar el mensaje con el nombre de usuario al servidor WebSocket
        lws_write(wsi, buffer + LWS_PRE, strlen(json), LWS_WRITE_TEXT);

        free(buffer);
        free(json); 
    }

    // Crear un hilo para leer mensajes
    pthread_t hilo_lectura;
    pthread_create(&hilo_lectura, NULL, leer_mensajes, (void*)wsi);

    // Bucle principal para mantener la conexión abierta
    while (connection_open) {
        lws_service(context, 100);  // Continuar procesando la conexión
    }

    pthread_join(hilo_lectura, NULL);

    lws_context_destroy(context);
    return 0;
}
