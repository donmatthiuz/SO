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
#include "parser.h"
#include <pthread.h>
#include <signal.h>

static int connection_open = 0;             // 1 si está conectado, 0 si no
static char nombre_usuario_global[50] = ""; // Nombre del usuario actual

const char *buscar_valor_por_clave(JsonPair *pares, int cantidad, const char *clave)
{
    for (int i = 0; i < cantidad; i++)
    {
        if (strcmp(pares[i].key, clave) == 0)
        {
            return pares[i].value;
        }
    }
    return "";
}

void mostrar_mensaje_formateado(const char *json)
{
    JsonPair pares[10];
    int n = parse_json(json, pares, 10);

    const char *type = buscar_valor_por_clave(pares, n, "type");
    const char *sender = buscar_valor_por_clave(pares, n, "sender");
    const char *content = buscar_valor_por_clave(pares, n, "content");
    const char *timestamp = buscar_valor_por_clave(pares, n, "timestamp");

    // Verificar si el mensaje es enviado por el usuario actual (you)
    const char *you_label = (strcmp(sender, nombre_usuario_global) == 0) ? " (you)" : "";

    const char *color_broadcast = "\033[1;33m"; // Amarillo para mensajes de difusión
    const char *color_private = "\033[1;36m";   // Azul claro para mensajes privados
    const char *color_you = "\033[1;32m";       // Verde suave para los mensajes de "you"
    const char *color_reset = "\033[0m";        // Reset de color

    if (strcmp(type, "broadcast") == 0)
    {
        // Si es "you", cambiar color
        if (strcmp(sender, nombre_usuario_global) == 0)
        {
            printf("\n>>> \033[1;34m[YOU] \033[0m\033[1;32m%s\033[0m: \033[1;36m%s\033[0m\n", sender, content);
        }
        else
        {
            printf("\n\033[1;34m[BROADCAST]\033[0m \033[1;32m%s\033[0m: %s\n", sender, content);
        }
    }
    else if (strcmp(type, "private") == 0)
    {
        // Para mensajes privados con tabulación y colores distintos
        if (strcmp(sender, nombre_usuario_global) == 0)
        {
            printf("\n\t\033[1;34m[YOU] \033[0m\033[1;35m%s\033[0m: %s\n", sender, content);
        }
        else
        {
            printf("\n\t\033[1;35m[PRIVATE] \033[0m\033[1;32m%s\033[0m: %s\n", sender, content);
        }
    }
    else if (strcmp(type, "list_response") == 0)
    {
        printf("\n\033[1;36m[USUARIOS CONECTADOS]\033[0m: %s\n", content);
    }
    else if (strcmp(type, "user_info") == 0)
    {
        printf("\n\033[1;36m[INFO USUARIO]\033[0m: %s\n", content);
    }
    else if (strcmp(type, "change_status") == 0)
    {
        printf("\n\033[1;33m[ESTADO CAMBIADO]\033[0m \033[1;32m%s\033[0m%s: %s\n", sender, you_label, content);
    }
    else if (strcmp(type, "disconnect") == 0)
    {
        printf("\n\033[1;31m[DESCONECTADO]\033[0m \033[1;32m%s\033[0m%s\n", sender, you_label);
    }
    else if (strcmp(type, "register") == 0)
    {
        // Ignorar mensaje de registro
        return;
    }
    else
    {
        printf("\n\033[1;37m[OTRO]\033[0m %s\n", json);
    }

    // Asegurar que el cursor se mantenga al final
    printf("> ");
    fflush(stdout);
}

// Función para obtener la IP local del equipo
char *get_local_ip()
{
    char hostbuffer[256];
    struct hostent *host_entry;
    int hostname;

    // Obtener el nombre del host
    hostname = gethostname(hostbuffer, sizeof(hostbuffer));
    if (hostname == -1)
    {
        perror("gethostname failed");
        return NULL;
    }

    // Obtener la información del host
    host_entry = gethostbyname(hostbuffer);
    if (host_entry == NULL)
    {
        perror("gethostbyname failed");
        return NULL;
    }

    // Obtener la dirección IP y convertirla a string
    struct in_addr *address = (struct in_addr *)host_entry->h_addr_list[0];
    return inet_ntoa(*address);
}

// Función de callback para manejar eventos de WebSocket
static int callback_client(struct lws *wsi, enum lws_callback_reasons reason, void *user, void *in, size_t len)
{
    switch (reason)
    {
    case LWS_CALLBACK_CLIENT_ESTABLISHED:
        printf("Conexión establecida con el servidor WebSocket\n");
        connection_open = 1; // Marcar que la conexión está abierta
        break;

    case LWS_CALLBACK_CLIENT_RECEIVE:
        mostrar_mensaje_formateado((char *)in);
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

// Definición del protocolo WebSocket
static struct lws_protocols protocols[] = {
    {"chat-protocol", callback_client, 0, 4096},
    {NULL, NULL, 0, 0}};

// Función que permite al usuario leer y enviar mensajes
void *leer_mensajes(void *arg)
{
    struct lws *wsi = (struct lws *)arg;
    char user_input[256];

    while (connection_open)
    {
        printf("> ");
        if (fgets(user_input, sizeof(user_input), stdin))
        {
            user_input[strcspn(user_input, "\n")] = 0; // Eliminar el salto de línea

            char *json = NULL;

            // Procesar comandos específicos del usuario
            if (strncmp(user_input, "/broadcast ", 11) == 0)
            {
                json = crearJson_broadcast(nombre_usuario_global, user_input + 11);
            }
            else if (strncmp(user_input, "/private ", 9) == 0)
            {
                char *space = strchr(user_input + 9, ' ');
                if (space)
                {
                    *space = '\0';
                    char *dest = user_input + 9;
                    char *msg = space + 1;
                    json = crearJson_private(nombre_usuario_global, dest, msg);
                }
            }
            else if (strncmp(user_input, "/list", 5) == 0)
            {
                json = crearJson_list_users(nombre_usuario_global);
            }
            else if (strncmp(user_input, "/info ", 6) == 0)
            {
                json = crearJson_user_info(nombre_usuario_global, user_input + 6);
            }
            else if (strncmp(user_input, "/status ", 8) == 0)
            {
                json = crearJson_change_status(nombre_usuario_global, user_input + 8);
            }
            else if (strncmp(user_input, "/exit", 5) == 0)
            {
                json = crearJson_disconnect(nombre_usuario_global);
                connection_open = 0;
            }
            else
            {
                json = crearJson_broadcast(nombre_usuario_global, user_input);
            }

            // Enviar mensaje si es válido
            if (json && strlen(json) > 0)
            {
                unsigned char *buffer = (unsigned char *)calloc(1, LWS_PRE + strlen(json));
                if (!buffer)
                {
                    printf("Error al asignar memoria\n");
                    return NULL;
                }

                memcpy(buffer + LWS_PRE, json, strlen(json));
                lws_write(wsi, buffer + LWS_PRE, strlen(json), LWS_WRITE_TEXT);

                free(buffer);
                free(json);
            }
        }
    }
    return NULL;
}

int main()
{
    // Cargar variables de entorno desde el archivo .env
    const char *archivo = ".env";
    VariableEntorno *variables = NULL;
    int cantidad = cargar_variables_entorno(archivo, &variables);
    if (cantidad < 0)
    {
        printf("Error al cargar las variables de entorno\n");
        return 1;
    }

    struct lws_context_creation_info info = {0};
    struct lws_context *context;
    struct lws *wsi;

    // Obtener la IP local
    char *local_ip = get_local_ip();
    if (local_ip == NULL)
    {
        printf("No se pudo obtener la IP local\n");
        return -1;
    }

    // Configuración del contexto WebSocket
    info.port = CONTEXT_PORT_NO_LISTEN;
    info.protocols = protocols;

    context = lws_create_context(&info);
    if (!context)
    {
        printf("Error creando el contexto WebSocket\n");
        return -1;
    }

    printf("Cliente WebSocket intentando conectarse a ws://%s:%s/chat\n", variables[0].valor, variables[1].valor);

    struct lws_client_connect_info ccinfo = {0};
    ccinfo.context = context;
    ccinfo.address = variables[0].valor; // Dirección del servidor
    ccinfo.port = atoi(variables[1].valor);
    ccinfo.path = "/";
    ccinfo.protocol = "chat-protocol";
    ccinfo.origin = local_ip; // Asignar la IP local al campo origin

    // Conectar al servidor WebSocket
    wsi = lws_client_connect_via_info(&ccinfo);
    if (!wsi)
    {
        printf("Error al intentar conectar al servidor\n");
        lws_context_destroy(context);
        return -1;
    }

    // Esperar hasta que la conexión se haya establecido
    while (!connection_open)
    {
        lws_service(context, 100);
        printf("Esperando a que la conexión se establezca...\n");
        usleep(100000);
    }

    // Solicitar nombre de usuario
    printf("Escribe tu usuario: ");
    if (fgets(nombre_usuario_global, sizeof(nombre_usuario_global), stdin))
    {
        nombre_usuario_global[strcspn(nombre_usuario_global, "\n")] = 0; // Eliminar salto de línea
    }

    // Enviar nombre de usuario al servidor
    char *json = crearJson_register(nombre_usuario_global);
    if (json && strlen(json) > 0)
    {
        unsigned char *buffer = (unsigned char *)calloc(1, LWS_PRE + strlen(json));
        if (!buffer)
        {
            printf("Error al asignar memoria\n");
            return -1;
        }

        memcpy(buffer + LWS_PRE, json, strlen(json));
        lws_write(wsi, buffer + LWS_PRE, strlen(json), LWS_WRITE_TEXT);

        free(buffer);
        free(json);
    }

    // Crear un hilo para la lectura de mensajes
    pthread_t hilo_lectura;
    pthread_create(&hilo_lectura, NULL, leer_mensajes, (void *)wsi);

    // Bucle principal para mantener la conexión
    while (connection_open)
    {
        lws_service(context, 100);
    }

    pthread_join(hilo_lectura, NULL);
    lws_context_destroy(context);
    return 0;
}
