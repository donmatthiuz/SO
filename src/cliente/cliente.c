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

// Variable global para controlar el estado de la conexión
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

        case LWS_CALLBACK_CLIENT_RECEIVE:
            printf("Respuesta del servidor: %s\n", (char *)in);
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

int main() {
    //obtenemos la ip del servidor
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

    
    printf("Conexión establecida. Ahora puedes enviar mensajes.\n");

    while (connection_open) {
        
        char user_input[256];
        printf("Escribe un mensaje para enviar al servidor: ");
        if (fgets(user_input, sizeof(user_input), stdin)) {
           
            user_input[strcspn(user_input, "\n")] = 0;

            
            if (strlen(user_input) > 0) {
                unsigned char *buffer = (unsigned char *)calloc(1,LWS_PRE + strlen(user_input));
                if (!buffer) {
                    printf("Error al asignar memoria\n");
                    continue;
                }

                
                memcpy(buffer + LWS_PRE, user_input, strlen(user_input));
                lws_write(wsi, buffer + LWS_PRE, strlen(user_input), LWS_WRITE_TEXT);

                free(buffer);
            }
        }
    }

    lws_context_destroy(context);
    return 0;
}
