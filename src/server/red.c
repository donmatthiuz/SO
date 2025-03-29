#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libwebsockets.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include "parser.h"
#include <stdbool.h>

#define MAX_CLIENTS 100
#define MAX_USUARIOS 100
#define TIEMPO_INACTIVIDAD 80


UsuarioRegistrado usuarios[MAX_USUARIOS];
volatile int force_exit = 0;
pthread_mutex_t mutex;
const char *estado_to_string(int status)
{
    switch (status)
    {
    case 0:
        return "ACTIVO";
    case 1:
        return "OCUPADO";
    case 2:
        return "INACTIVO";
    default:
        return "DESCONOCIDO";
    }
}
struct per_session_data
{
    char client_id[50];
    char client_ip[50];
    struct lws *wsi;
    int is_active;
};

struct per_session_data clients[MAX_CLIENTS];

char *get_current_timestamp()
{
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    char *buf = malloc(32);
    strftime(buf, 32, "%Y-%m-%d %H:%M:%S", t);
    return buf;
}



void *monitor_inactividad(void *arg)
{
    while (!force_exit)
    {
        time_t ahora = time(NULL);

        pthread_mutex_lock(&mutex);
        for (int i = 0; i < MAX_USUARIOS; i++)
        {
            if (usuarios[i].activo && usuarios[i].status != 2) // revisa si esta ya inactivo
            {
                if (difftime(ahora, usuarios[i].ultima_actividad) >= TIEMPO_INACTIVIDAD)//60 segundos sin actividad dice inactivo
                {
                    usuarios[i].status = 2;
                    printf("[INACTIVIDAD] Usuario %s marcado como INACTIVO\n", usuarios[i].nombre);
                }
            }
        }
        pthread_mutex_unlock(&mutex);

        sleep(10); //el hilo revisa estas veces
    }
    return NULL;
}


bool registrar_usuario(const char *nombre, const char *ip, struct lws *wsi)
{
    int encontrado = 0;
    char *timestamp = get_current_timestamp();
    for (int i = 0; i < MAX_USUARIOS; i++)
    {
        
        if ( strcmp(usuarios[i].ip, ip) == 0)
        {
            encontrado = 1;
        
            if (strcmp(usuarios[i].nombre, nombre) == 0)
            {
                usuarios[i].activo = 1;
                usuarios[i].wsi = wsi;
                usuarios[i].status = 0;
                printf("[INFO] Usuario '%s' reactivado en la IP: %s\n", nombre, ip);
                return true;  // Registro exitoso, se reactiva el usuario
            }
            else
            {

                if (i < MAX_USUARIOS && usuarios[i].nombre != NULL) {
                    if (strcmp(usuarios[i].ip, ip) == 0) {
                        if (strcmp(usuarios[i].nombre, nombre) != 0) {
                            char *json_error = crearjsonError("server", timestamp, "Ya tiene un nombre de usuario con esta ip");
                            send_to_unknow_client(json_error, wsi);
                            printf("[ERROR] Conflicto de nombres. La IP '%s' ya está registrada con el usuario '%s'.\n", ip, usuarios[i].nombre);
                            usuarios[i].activo = 0;
                        } else {

                        }
                    }
                }

                return false;  
            }
        }
    }

    if (!encontrado){
        for (int i = 0; i < MAX_USUARIOS; i++)
        {
            
            
                
                strncpy(usuarios[i].nombre, nombre, sizeof(usuarios[i].nombre));
                strncpy(usuarios[i].ip, ip, sizeof(usuarios[i].ip));
                usuarios[i].wsi = wsi;
                usuarios[i].status = 0; // Asignar el estado inicial del usuario
                usuarios[i].activo = 1;
                printf("[INFO] Usuario '%s' registrado en la IP: %s\n", nombre, ip);
                return true;  
            
        }

    }

    
    printf("[ERROR] No hay espacio para más usuarios.\n");
    free(timestamp);
    return false; 
}

void sighandler(int sig)
{
    force_exit = 1;
}

void send_to_specific_client  (const char *target_name, const char *message, const char *sender_name)
{
    int encontrado = 0;
    for (int i = 0; i < MAX_USUARIOS; i++)
    {
        if (usuarios[i].activo && strcmp(usuarios[i].nombre, target_name) == 0)
        {
            int message_len = strlen(message);
            unsigned char *buf = malloc(LWS_PRE + message_len);
            if (!buf)
            {
                printf("Memory allocation error\n");
                return;
            }

            memcpy(buf + LWS_PRE, message, message_len);
            printf("[INFO] Enviando mensaje a %s: %s\n", target_name, message);
            lws_write(usuarios[i].wsi, buf + LWS_PRE, message_len, LWS_WRITE_TEXT);

            free(buf);
            return;
        }
    }
    if (!encontrado && sender_name != ""){
        char *timestamp = get_current_timestamp();
        char *json = crearjsonError("server", timestamp,  "Usuario no encontrado");
        send_to_specific_client(sender_name, json, "");
    }
    printf("[WARN] Cliente '%s' no encontrado\n", target_name);
}




void send_to_unknow_client  (const char *message, struct lws *wsi)
{
    int message_len = strlen(message);
    unsigned char *buf = malloc(LWS_PRE + message_len);
    if (!buf)
    {
        printf("Memory allocation error\n");
        return;
    }

    memcpy(buf + LWS_PRE, message, message_len);
    printf("[INFO] Enviando mensaje a usuario desconocido : %s \n",  message);
    lws_write(wsi, buf + LWS_PRE, message_len, LWS_WRITE_TEXT);

    free(buf);
}

void *client_thread(void *arg)
{
    struct per_session_data *pss = (struct per_session_data *)arg;
    printf("Manejando cliente: %s\n", pss->client_id);

    while (pss->is_active)
    {
        usleep(1000);
    }

    pthread_mutex_lock(&mutex);
    for (int i = 0; i < MAX_CLIENTS; i++)
    {
        if (strcmp(clients[i].client_id, pss->client_id) == 0)
        {
            clients[i].is_active = 0;
            break;
        }
    }
    pthread_mutex_unlock(&mutex);

    printf("Hilo terminado para cliente: %s\n", pss->client_id);
    return NULL;
}

void actualizar_estado_usuario(const char *nombre, const char *nuevo_estado)
{
    
    for (int i = 0; i < MAX_USUARIOS; i++)
    {
        if (usuarios[i].activo && strcmp(usuarios[i].nombre, nombre) == 0)
        {
            if (strcmp(nuevo_estado, "OCUPADO") == 0)
                usuarios[i].status = 1;
            else if (strcmp(nuevo_estado, "INACTIVO") == 0)
                usuarios[i].status = 2;
            else
                usuarios[i].status = 0;
        }
    }
}

char *crearJson_info_usuario(const char *nombre_objetivo)
{
    char *timestamp = get_current_timestamp();
    int encontrado = 0;
    for (int i = 0; i < MAX_USUARIOS; i++)
    {
        if (usuarios[i].activo && strcmp(usuarios[i].nombre, nombre_objetivo) == 0)
        {
            
            if (!timestamp)
                return NULL;

            int size = snprintf(NULL, 0,
                                "{\"type\":\"user_info_response\",\"sender\":\"server\",\"target\":\"%s\",\"content\":{\"ip\":\"%s\",\"status\":\"%s\"},\"timestamp\":\"%s\"}",
                                usuarios[i].nombre, usuarios[i].ip, estado_to_string(usuarios[i].status), timestamp) +
                       1;

            char *json = (char *)malloc(size);
            if (!json)
            {
                free(timestamp);
                return NULL;
            }

            snprintf(json, size,
                     "{\"type\":\"user_info_response\",\"sender\":\"server\",\"target\":\"%s\",\"content\":{\"ip\":\"%s\",\"status\":\"%s\"},\"timestamp\":\"%s\"}",
                     usuarios[i].nombre, usuarios[i].ip, estado_to_string(usuarios[i].status), timestamp);

            free(timestamp);
            return json;
        }
    }

    if (!encontrado)
    {
        char *json;
        
        json = crearjsonError("server", timestamp, "No se encontro informacion del usuario");
    }
    // Usuario no encontrado
    
}

char *crearJson_lista_usuarios()
{
    char buffer[1024] = "{\"type\":\"list_users_response\",\"sender\":\"server\",\"content\":[";
    int first = 1;

    for (int i = 0; i < MAX_USUARIOS; i++)
    {
        if (usuarios[i].activo)
        {
            if (!first)
                strcat(buffer, ",");
            char temp[100];
            snprintf(temp, sizeof(temp), "\"%s\"", usuarios[i].nombre);
            strcat(buffer, temp);
            first = 0;
        }
    }

    strcat(buffer, "],\"timestamp\":\"");

    char *timestamp = get_current_timestamp();
    strcat(buffer, timestamp);
    strcat(buffer, "\"}");

    free(timestamp);
    return strdup(buffer);
}





static int callback_chat(struct lws *wsi, enum lws_callback_reasons reason,
                         void *user, void *in, size_t len)
{
    struct per_session_data *pss = (struct per_session_data *)user;

    switch (reason)
    {
    case LWS_CALLBACK_ESTABLISHED:
    {
        lws_get_peer_simple(wsi, pss->client_ip, sizeof(pss->client_ip));
        snprintf(pss->client_id, sizeof(pss->client_id) - 1, "user_%.40s", pss->client_ip);
        pss->client_id[sizeof(pss->client_id) - 1] = '\0';
        pss->wsi = wsi;
        pss->is_active = 1;

        pthread_mutex_lock(&mutex);
        for (int i = 0; i < MAX_CLIENTS; i++)
        {
            if (!clients[i].is_active)
            {
                memcpy(&clients[i], pss, sizeof(struct per_session_data));
                break;
            }
        }
        pthread_mutex_unlock(&mutex);

        printf("\033[1;32m[+] Cliente conectado: %s\033[0m\n", pss->client_id);

        pthread_t thread;
        if (pthread_create(&thread, NULL, client_thread, pss) != 0)
        {
            printf("[ERROR] Hilo no creado para cliente %s\n", pss->client_id);
        }
        else
        {
            pthread_detach(thread);
        }
        break;
    }

    case LWS_CALLBACK_RECEIVE:
    
    {
        char message[len + 1];
        memcpy(message, in, len);
        message[len] = '\0';

        char json_extraido[256];
        extract_json(message, json_extraido);

        JsonPair pares[10];
        int n = parse_json(json_extraido, pares, 10);

        char tipo[50] = "";
        char sender[50] = "";

        for (int i = 0; i < n; i++)
        {
            if (strcmp(pares[i].key, "type") == 0)
                strncpy(tipo, pares[i].value, sizeof(tipo));
            else if (strcmp(pares[i].key, "sender") == 0)
                strncpy(sender, pares[i].value, sizeof(sender));
        }

        
        for (int i = 0; i < MAX_USUARIOS; i++)
            {
                if (usuarios[i].activo && strcmp(usuarios[i].nombre, sender) == 0)
                {
                    usuarios[i].ultima_actividad = time(NULL);
                    break;
                }
        }

        if (strcmp(tipo, "register") == 0)
        {
            char *timestamp = get_current_timestamp();
            bool exito = registrar_usuario(sender, pss->client_ip, wsi);

            if (exito)  {///
                char *json = crearJson_Registro_Exitoso("mathew", timestamp, usuarios, MAX_USUARIOS);


                // Notificar a todos los usuarios que un nuevo usuario se ha registrado
                char mensaje_nuevo_usuario[256];
                char *json2 = crearJson_Brodcast_register("server", timestamp, sender);

                snprintf(mensaje_nuevo_usuario, sizeof(mensaje_nuevo_usuario), "%s", json2);

                //printf(mensaje_nuevo_usuario);
                pthread_mutex_lock(&mutex);
                for (int i = 0; i < MAX_USUARIOS; i++)
                {
                    if (usuarios[i].activo && usuarios[i].wsi != wsi) // Evitar enviarlo al mismo cliente que se registró
                    {
                        
                        send_to_specific_client(usuarios[i].nombre, mensaje_nuevo_usuario, "server");
                        printf("[INFO] Mensaje de registro enviado a %s\n", usuarios[i].nombre);
                    }
                }

                char mensaje[256]; // Ajusta el tamaño si es necesario
            
                

                strncpy(mensaje, json, sizeof(mensaje) - 1);
                mensaje[sizeof(mensaje) - 1] = '\0';
                
                send_to_specific_client(sender, mensaje, sender);
                pthread_mutex_unlock(&mutex);

            }//
        }

        else if (strcmp(tipo, "broadcast") == 0)
        {
            const char *mensaje = getValueByKey(pares, n, "content");
            printf("[BROADCAST] %s: %s\n", sender, mensaje);

            pthread_mutex_lock(&mutex);
            for (int i = 0; i < MAX_USUARIOS; i++)
            {
                if (usuarios[i].activo && usuarios[i].wsi != wsi) // Evitar enviarlo al mismo cliente que lo envió
                {
                    int len_msg = strlen(message);
                    unsigned char *buf = malloc(LWS_PRE + len_msg);
                    if (!buf)
                    {
                        printf("[ERROR] Memoria insuficiente para broadcast\n");
                        continue;
                    }
                    memcpy(buf + LWS_PRE, message, len_msg);
                    lws_write(usuarios[i].wsi, buf + LWS_PRE, len_msg, LWS_WRITE_TEXT);
                    free(buf);
                    printf("[INFO] Mensaje broadcast enviado a %s\n", usuarios[i].nombre);
                }
            }
            pthread_mutex_unlock(&mutex);
        }

        else if (strcmp(tipo, "private") == 0)
        {
            const char *destino = getValueByKey(pares, n, "target");
            if (destino)
            {   
                // Verifica si el mensaje ya fue enviado a este destinatario
                printf("[PRIVATE] Enviando mensaje a %s\n", destino);
                pthread_mutex_lock(&mutex);
                send_to_specific_client(destino, message, sender);
                pthread_mutex_unlock(&mutex);
            }
        }

        else if (strcmp(tipo, "list_users") == 0)
        {   
            pthread_mutex_lock(&mutex);
            printf("[LISTA] %s pidió la lista de usuarios\n", sender);
            char *respuesta = crearJson_lista_usuarios();
            send_to_specific_client(sender, respuesta, sender);
            free(respuesta);
            pthread_mutex_unlock(&mutex);
            
        }

        else if (strcmp(tipo, "user_info") == 0)
        {
            pthread_mutex_lock(&mutex);
            const char *target = getValueByKey(pares, n, "target");
            char *respuesta = crearJson_info_usuario(target);
            send_to_specific_client(sender, respuesta, sender);
            free(respuesta);
            pthread_mutex_unlock(&mutex);
        }

        else if (strcmp(tipo, "change_status") == 0)
        {
            
            pthread_mutex_lock(&mutex);
            char *timestamp = get_current_timestamp();
            const char *nuevo_estado = getValueByKey(pares, n, "content");
            actualizar_estado_usuario(sender, nuevo_estado);
            char *json_sender = crearJsonCambi_status_server("server",timestamp,  nuevo_estado, sender);
            send_to_specific_client(sender,json_sender, "server");
            pthread_mutex_unlock(&mutex);
        }

        else if (strcmp(tipo, "disconnect") == 0)
        {
            pthread_mutex_lock(&mutex);
            printf("[DESCONECTAR] %s cerró sesión\n", sender);
            lws_close_reason(wsi, LWS_CLOSE_STATUS_NORMAL, NULL, 0);
            lws_callback_on_writable(wsi);
            pthread_mutex_unlock(&mutex);
        }

        
        if (!(strcmp(tipo, "list_users") == 0 || strcmp(tipo, "user_info") == 0))
        {
            pthread_mutex_lock(&mutex);
            printf("\033[1;34m[Mensaje] de %s:\033[0m %s\n", pss->client_ip, message);
            send_to_specific_client(sender, message, sender);
            pthread_mutex_unlock(&mutex);
        }

        break;
    }

    case LWS_CALLBACK_CLOSED:
    {
        pthread_mutex_lock(&mutex);
        for (int i = 0; i < MAX_CLIENTS; i++)
        {
            if (strcmp(clients[i].client_id, pss->client_id) == 0)
            {
                clients[i].is_active = 0;
                break;
            }
        }
        pss->is_active = 0;
        pthread_mutex_unlock(&mutex);
        printf("\033[1;31m[-] Cliente desconectado: %s\033[0m\n", pss->client_id);
        
        break;
    }

    default:
        break;
    }
    return 0;
}

static struct lws_protocols protocols[] = {
    {"chat-protocol", callback_chat, sizeof(struct per_session_data), 4096},
    {NULL, NULL, 0, 0}};

int main()
{
    signal(SIGINT, sighandler);

    struct lws_context_creation_info info = {0};
    struct lws_context *context;

    memset(clients, 0, sizeof(clients));

    info.port = 5000;
    info.protocols = protocols;
    info.gid = -1;
    info.uid = -1;

    if (pthread_mutex_init(&mutex, NULL) != 0)
    {
        printf("[ERROR] Mutex no inicializado\n");
        return -1;
    }

    context = lws_create_context(&info);
    if (!context)
    {
        printf("[ERROR] Contexto WebSocket no creado\n");
        pthread_mutex_destroy(&mutex);
        return -1;
    }

    pthread_t hilo_inactividad;
    if (pthread_create(&hilo_inactividad, NULL, monitor_inactividad, NULL) != 0)
    {
        printf("[ERROR] No se pudo crear el hilo de inactividad\n");
    }
    else
    {
        pthread_detach(hilo_inactividad);
    }


    printf("\n\033[1;36mServidor WebSocket en ws://localhost:5000/\033[0m\n\n");

    while (!force_exit)
    {
        lws_service(context, 50);
    }

    printf("\033[1;33m[!] Cerrando servidor...\033[0m\n");
    pthread_mutex_destroy(&mutex);
    lws_context_destroy(context);
    return 0;
}