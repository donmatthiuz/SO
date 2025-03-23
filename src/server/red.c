#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libwebsockets.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>

volatile int force_exit = 0;

// Estructura para datos de sesión
struct per_session_data {
    char client_ip[50]; 
    pthread_t thread_id;
};


struct thread_data {
    struct lws_context *context;
};

// Manejador de señales
void sighandler(int sig) {
    force_exit = 1;
}


void *client_thread(void *data) {
    struct thread_data *td = (struct thread_data *)data;

    while (lws_service(td->context, 50) >= 0 && !force_exit);

    printf("Hilo de cliente terminado\n");
    free(td);
    pthread_exit(NULL);
}

// Callback del WebSocket
static int callback_chat(struct lws *wsi, enum lws_callback_reasons reason, 
                         void *user, void *in, size_t len) {
    struct per_session_data *pss = (struct per_session_data *)user;

    switch (reason) {
        case LWS_CALLBACK_ESTABLISHED: {
            printf("Cliente conectado\n");
            lws_get_peer_simple(wsi, pss->client_ip, sizeof(pss->client_ip));

            // Crear datos del hilo
            struct thread_data *td = malloc(sizeof(struct thread_data));
            if (!td) {
                printf("Error al asignar memoria para el thread\n");
                return -1;
            }

            td->context = lws_get_context(wsi);

           
            if (pthread_create(&pss->thread_id, NULL, client_thread, (void *)td) != 0) {
                printf("Error al crear el hilo\n");
                free(td);
                return -1;
            }

            printf("Hilo creado para %s\n", pss->client_ip);
            break;
        }

        case LWS_CALLBACK_RECEIVE: {
            char message[len + 1];
            memcpy(message, in, len);
            message[len] = '\0';

            printf("Mensaje de %s: %s\n", pss->client_ip, message);
            break;
        }

        case LWS_CALLBACK_CLOSED:
            printf("Cliente %s desconectado\n", pss->client_ip);
            pthread_cancel(pss->thread_id); // Terminar el hilo
            break;

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

    info.port = 5000;
    info.protocols = protocols;
    info.gid = -1;
    info.uid = -1;

    context = lws_create_context(&info);
    if (!context) {
        printf("Error creando el contexto WebSocket\n");
        return -1;
    }

    printf("Servidor WebSocket en ws://localhost:5000/\n");

    while (!force_exit) {
        lws_service(context, 50);
    }

    printf("Cerrando servidor...\n");
    lws_context_destroy(context);

    return 0;
}
