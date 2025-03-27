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
#include <cjson/cJSON.h>

static int connection_open = 0;
static char nombre_usuario_global[50] = "";

const char *color_info = "\033[1;36m";
const char *color_wait = "\033[1;33m";
const char *color_user_input = "\033[1;32m";
const char *color_error = "\033[1;31m";

const char *color_labels = "\033[1;36m";        // celeste
const char *color_message = "\033[1;37m";       // blanco
const char *color_private_label = "\033[1;35m"; // rosa
const char *color_other_user = "\033[1;33m";    // amarillo
const char *color_my_user = "\033[1;32m";       // verde
const char *color_desconection = "\033[1;31m";  // rojo
const char *color_input = "\033[1;30m";         // gris
const char *color_reset = "\033[0m";

/*
    Devuelve el valor asociado a una clave de un dataset clave-valor, si no existe devuelve vacío
*/
const char *getValueByKey(JsonPair *pares, int cantidad, const char *clave)
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

/*
    Recibe un json y lo muestra de una mejor forma de acuerdo al tipo de mensaje
*/
void showFormattedMessage(const char *json)
{
    cJSON *root = cJSON_Parse(json);
    if (!root)
    {
        printf("[ERROR] No se pudo parsear el JSON\n");
        return;
    }

    const cJSON *typeObj = cJSON_GetObjectItem(root, "type");
    const char *type = typeObj ? typeObj->valuestring : "";

    const cJSON *senderObj = cJSON_GetObjectItem(root, "sender");
    const char *sender = senderObj ? senderObj->valuestring : "";

    const cJSON *timestampObj = cJSON_GetObjectItem(root, "timestamp");
    const char *timestamp = timestampObj ? timestampObj->valuestring : "";

    const cJSON *contentObj = cJSON_GetObjectItem(root, "content");

    const char *you_label = (strcmp(sender, nombre_usuario_global) == 0) ? "(YOU)" : "";

    if (strcmp(type, "list_users_response") == 0)
    {
        printf("\n%s[USUARIOS CONECTADOS - %s]%s:", color_labels, timestamp, color_reset);

        if (contentObj && cJSON_IsArray(contentObj))
        {
            cJSON *user;
            cJSON_ArrayForEach(user, contentObj)
            {
                if (cJSON_IsString(user))
                {
                    printf("\n\t%s- %s%s", color_message, user->valuestring, color_reset);
                }
            }
        }

        printf("\n\n\t%s> ", color_input);
        fflush(stdout);
        cJSON_Delete(root);
        return;
    }

    if (strcmp(type, "register") == 0)
    {
        if (strcmp(sender, nombre_usuario_global) == 0)
        {
            printf("\n%s[USUARIO NUEVO]%s %s%s te has unido al chat.%s\n", color_labels, color_reset, color_my_user, sender, color_reset);
        }
        else
        {
            printf("\n%s[USUARIO NUEVO]%s %s%s se ha unido al chat.%s\n", color_labels, color_reset, color_other_user, sender, color_reset);
        }
    }

    else if (strcmp(type, "broadcast") == 0)
    {
        const char *msg = contentObj ? contentObj->valuestring : "";
        if (strcmp(sender, nombre_usuario_global) == 0)
        {
            printf("\n%s[BROADCAST - %s] %s%s (YOU): %s%s%s", color_labels, timestamp, color_my_user, sender, color_reset, color_message, msg);
        }
        else
        {
            printf("\n%s[BROADCAST - %s] %s%s: %s%s", color_labels, timestamp, color_other_user, sender, color_message, msg);
        }
    }

    else if (strcmp(type, "private") == 0)
    {
        const char *msg = contentObj ? contentObj->valuestring : "";
        if (strcmp(sender, nombre_usuario_global) == 0)
        {
            printf("\n\t%s[PRIVATE - %s] %s%s (YOU): %s%s%s", color_private_label, timestamp, color_my_user, sender, color_reset, color_message, msg);
        }
        else
        {
            printf("\n\t%s[PRIVATE - %s] %s%s: %s%s", color_private_label, timestamp, color_other_user, sender, color_message, msg);
        }
    }

    else if (strcmp(type, "user_info_response") == 0)
    {
        const char *target = cJSON_GetObjectItem(root, "target")->valuestring;
        cJSON *content = cJSON_GetObjectItem(root, "content");
        const char *ip = cJSON_GetObjectItem(content, "ip")->valuestring;
        const char *status = cJSON_GetObjectItem(content, "status")->valuestring;

        printf("\n%s[INFO USUARIO - %s]%s", color_labels, timestamp, color_reset);
        printf("\n\t- %sUSER:%s %s", color_labels, color_reset, target);
        printf("\n\t- %sIP:%s %s", color_labels, color_reset, ip);
        printf("\n\t- %sSTATUS:%s %s", color_labels, color_reset, status);
    }

    else if (strcmp(type, "change_status") == 0)
    {
        const char *msg = contentObj ? contentObj->valuestring : "";
        printf("\n%s[ESTADO CAMBIADO]%s %s%s: %s", color_desconection, color_reset, color_my_user, sender, msg);
    }

    else if (strcmp(type, "disconnect") == 0)
    {
        printf("\n%s[DESCONECTADO]%s %s%s %s", color_desconection, color_reset, color_my_user, sender, you_label);
    }

    else
    {
        // printf("\n%s[OTRO]%s %s", color_reset, color_message, json);
    }

    printf("\n\n\t%s> ", color_input);
    fflush(stdout);
    cJSON_Delete(root);
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
        printf("%sConexión establecida con el servidor WebSocket%s\n", color_info, color_reset);
        connection_open = 1; // Marcar que la conexión está abierta
        break;

    case LWS_CALLBACK_CLIENT_RECEIVE:
        showFormattedMessage((char *)in);
        break;

    case LWS_CALLBACK_CLOSED:
        printf("%sConexión cerrada%s\n", color_info, color_reset);
        connection_open = 0; // Marcar que la conexión ha sido cerrada
        break;

    case LWS_CALLBACK_CLIENT_CONNECTION_ERROR:
        printf("%sError de conexión: %s%s\n", color_error, (char *)in, color_reset);
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
        // printf("> ");
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
        printf("%sError al cargar las variables de entorno%s\n", color_error, color_reset);
        return 1;
    }

    struct lws_context_creation_info info = {0};
    struct lws_context *context;
    struct lws *wsi;

    // Obtener la IP local
    char *local_ip = get_local_ip();
    if (local_ip == NULL)
    {
        printf("%sNo se pudo obtener la IP local%s\n", color_error, color_reset);
        return -1;
    }

    // Configuración del contexto WebSocket
    info.port = CONTEXT_PORT_NO_LISTEN;
    info.protocols = protocols;

    context = lws_create_context(&info);
    if (!context)
    {
        printf("%sError creando el contexto WebSocket%s\n", color_error, color_reset);
        return -1;
    }

    printf("%sCliente WebSocket intentando conectarse a ws://%s:%s/chat%s\n", color_info, variables[0].valor, variables[1].valor, color_reset);

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
        printf("%sError al intentar conectar al servidor%s\n", color_error, color_reset);
        lws_context_destroy(context);
        return -1;
    }

    // Esperar hasta que la conexión se haya establecido
    while (!connection_open)
    {
        lws_service(context, 100);
        printf("%sEsperando a que la conexión se establezca...%s\n", color_wait, color_reset);
        usleep(100000);
    }

    // Solicitar nombre de usuario
    printf("%sEscribe tu usuario: %s", color_user_input, color_input);
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
            printf("%sError al asignar memoria%s\n", color_error, color_reset);
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