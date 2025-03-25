#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libwebsockets.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>

#define MAX_CLIENTS 100

volatile int force_exit = 0;
pthread_mutex_t mutex;

struct per_session_data {
    char client_id[50];
    char client_ip[50];
    struct lws *wsi;
    int is_active;
};

struct per_session_data clients[MAX_CLIENTS];

// Added sighandler function
void sighandler(int sig) {
    force_exit = 1;
}

void send_to_specific_client(const char* target_id, const char* message) {
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (clients[i].is_active && 
            strcmp(clients[i].client_id, target_id) == 0) {
            
            int message_len = strlen(message);
            unsigned char *buf = malloc(LWS_PRE + message_len);
            if (!buf) {
                printf("Memory allocation error\n");
                pthread_mutex_unlock(&mutex);
                return;
            }

            memcpy(buf + LWS_PRE, message, message_len);
            printf("Enviando mensaje al cliente %s \n", message);
            lws_write(clients[i].wsi, buf + LWS_PRE, message_len, LWS_WRITE_TEXT);
            
            free(buf);
            break;
        } else {
            printf("Cliente no encontrado\n");
        }
    }
}

// Esta función se ejecutará en el hilo de cada cliente
void* client_thread(void *arg) {
    struct per_session_data *pss = (struct per_session_data*)arg;
    
    // Aquí puedes realizar la comunicación con el cliente, recibir y enviar mensajes
    printf("Manejando cliente: %s\n", pss->client_id);
    
    // Ejemplo de mantener el hilo en ejecución mientras el cliente está activo
    while (pss->is_active) {
        // Este bucle simula la espera de nuevos mensajes o el cierre de conexión
        usleep(1000); // Espera 1ms para evitar un bucle ocupado
    }

    // Cuando se termina de manejar la conexión, marcarlo como inactivo
    pthread_mutex_lock(&mutex);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (strcmp(clients[i].client_id, pss->client_id) == 0) {
            clients[i].is_active = 0;
            break;
        }
    }
    pthread_mutex_unlock(&mutex);

    printf("Hilo terminado para cliente: %s\n");
    return NULL;
}

static int callback_chat(struct lws *wsi, enum lws_callback_reasons reason,
                         void *user, void *in, size_t len) {
    struct per_session_data *pss = (struct per_session_data *)user;

    switch (reason) {
        case LWS_CALLBACK_ESTABLISHED: {
            lws_get_peer_simple(wsi, pss->client_ip, sizeof(pss->client_ip));
            snprintf(pss->client_id, sizeof(pss->client_id), "user_%s", pss->client_ip);
            pss->wsi = wsi;
            pss->is_active = 1;

            // Asignar el cliente al array
            pthread_mutex_lock(&mutex);
            for (int i = 0; i < MAX_CLIENTS; i++) {
                if (!clients[i].is_active) {
                    memcpy(&clients[i], pss, sizeof(struct per_session_data));
                    break;
                }
            }
            pthread_mutex_unlock(&mutex);

            printf("Cliente conectado: %s\n", pss->client_id);

            // Crear un hilo para manejar la comunicación con este cliente
            pthread_t thread;
            if (pthread_create(&thread, NULL, client_thread, pss) != 0) {
                printf("Error creando el hilo para el cliente %s\n", pss->client_id);
            } else {
                // Ya no necesitamos mantener el hilo activo, podemos detallar el thread después
                pthread_detach(thread);  // Si no vamos a esperar al hilo
            }
            break;
        }

        case LWS_CALLBACK_RECEIVE: {
            char message[len + 1];
            memcpy(message, in, len);
            message[len] = '\0';

            pthread_mutex_lock(&mutex);
            printf("Mensaje de %s: %s\n", pss->client_ip, message);
            send_to_specific_client("user_127.0.0.1", pss->client_id);
            pthread_mutex_unlock(&mutex);
            break;
        }

        case LWS_CALLBACK_CLOSED: {
            // Indicar que el cliente está inactivo
            pthread_mutex_lock(&mutex);
            for (int i = 0; i < MAX_CLIENTS; i++) {
                if (strcmp(clients[i].client_id, pss->client_id) == 0) {
                    clients[i].is_active = 0;
                    break;
                }
            }
            pthread_mutex_unlock(&mutex);
            printf("Cliente desconectado: %s\n", pss->client_id);
            pss->is_active = 0;  // Marcar como inactivo para que el hilo termine
            break;
        }

        default:
            break;
    }
    return 0;
}

static struct lws_protocols protocols[] = {
    { "chat-protocol", callback_chat, sizeof(struct per_session_data), 4096 },
    { NULL, NULL, 0, 0 }
};

int main() {
    signal(SIGINT, sighandler);

    struct lws_context_creation_info info = {0};
    struct lws_context *context;

    memset(clients, 0, sizeof(clients));

    info.port = 5000;
    info.protocols = protocols;
    info.gid = -1;
    info.uid = -1;

    if (pthread_mutex_init(&mutex, NULL) != 0) {
        printf("Error inicializando el mutex\n");
        return -1;
    }

    context = lws_create_context(&info);
    if (!context) {
        printf("Error creando el contexto WebSocket\n");
        pthread_mutex_destroy(&mutex);
        return -1;
    }

    printf("Servidor WebSocket en ws://localhost:5000/\n");

    while (!force_exit) {
        lws_service(context, 50);
    }

    printf("Cerrando servidor...\n");
    pthread_mutex_destroy(&mutex);
    lws_context_destroy(context);
    return 0;
}
