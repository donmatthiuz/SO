#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

typedef struct
{
    char key[50];
    char value[50];
    int isNumber;
} JsonPair;

/*
    Elimina espacios entre comillas evitando los espacios dentro de ella para mejor formato en JSON y sin perder el mensaje en el chat
*/
void remove_spaces(char *str)
{
    char *i = str, *j = str;
    int in_string = 0;

    while (*i != '\0')
    {
        if (*i == '"')
        {
            in_string = !in_string; // Alterna si está dentro de comillas
        }

        if (in_string || !isspace((unsigned char)*i))
        {
            *j++ = *i;
        }
        i++;
    }
    *j = '\0';
}

void extract_json(const char *input, char *output)
{
    int i = 0, j = 0;

    while (input[i] != '{' && input[i] != '\0')
    {
        i++;
    }

    if (input[i] == '\0')
    {
        output[0] = '\0';
        return;
    }

    int brace_count = 0;
    while (input[i] != '\0')
    {
        if (input[i] == '{')
            brace_count++;
        if (input[i] == '}')
            brace_count--;

        output[j++] = input[i++];

        if (brace_count == 0)
        {
            output[j] = '\0';
            return;
        }
    }

    output[0] = '\0';
}

int parse_json(const char *json_str, JsonPair *pairs, int max_pairs)
{
    char buffer[256];
    strncpy(buffer, json_str, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    remove_spaces(buffer);

    if (buffer[0] != '{' || buffer[strlen(buffer) - 1] != '}')
    {
        return -1;
    }

    int count = 0;
    char *token = strtok(buffer + 1, ",}");
    while (token && count < max_pairs)
    {
        char *colon = strchr(token, ':');
        if (!colon)
            return -1;
        *colon = '\0';
        strncpy(pairs[count].key, token + 1, strlen(token) - 2);
        pairs[count].key[strlen(token) - 2] = '\0';

        char *value = colon + 1;
        if (value[0] == '\"')
        {
            strncpy(pairs[count].value, value + 1, strlen(value) - 2);
            pairs[count].value[strlen(value) - 2] = '\0';
            pairs[count].isNumber = 0;
        }
        else
        {
            strncpy(pairs[count].value, value, sizeof(pairs[count].value) - 1);
            pairs[count].isNumber = 1;
        }

        count++;
        token = strtok(NULL, ",}");
    }

    return count;
}

char *crearJson_register(const char *nombre_usuario)
{

    int tamaño = snprintf(NULL, 0, "{\"type\": \"register\", \"sender\": \"%s\", \"content\": null}", nombre_usuario) + 1;

    char *resultado = (char *)malloc(tamaño);
    if (!resultado)
    {
        printf("Error al asignar memoria\n");
        return NULL;
    }

    snprintf(resultado, tamaño, "{\"type\": \"register\", \"sender\": \"%s\", \"content\": null}", nombre_usuario);

    return resultado;
}

char *crearJson_broadcast(const char *sender, const char *mensaje)
{
    int tamaño = snprintf(NULL, 0,
                          "{\"type\": \"broadcast\", \"sender\": \"%s\", \"content\": \"%s\", \"timestamp\": \"\"}",
                          sender, mensaje) +
                 1;

    char *resultado = (char *)malloc(tamaño);
    if (!resultado)
        return NULL;

    snprintf(resultado, tamaño,
             "{\"type\": \"broadcast\", \"sender\": \"%s\", \"content\": \"%s\", \"timestamp\": \"\"}",
             sender, mensaje);

    return resultado;
}

char *crearJson_private(const char *sender, const char *target, const char *mensaje)
{
    int tamaño = snprintf(NULL, 0,
                          "{\"type\": \"private\", \"sender\": \"%s\", \"target\": \"%s\", \"content\": \"%s\", \"timestamp\": \"\"}",
                          sender, target, mensaje) +
                 1;

    char *resultado = (char *)malloc(tamaño);
    if (!resultado)
        return NULL;

    snprintf(resultado, tamaño,
             "{\"type\": \"private\", \"sender\": \"%s\", \"target\": \"%s\", \"content\": \"%s\", \"timestamp\": \"\"}",
             sender, target, mensaje);

    return resultado;
}

char *crearJson_list_users(const char *sender)
{
    int tamaño = snprintf(NULL, 0,
                          "{\"type\": \"list_users\", \"sender\": \"%s\"}", sender) +
                 1;

    char *resultado = (char *)malloc(tamaño);
    if (!resultado)
        return NULL;

    snprintf(resultado, tamaño, "{\"type\": \"list_users\", \"sender\": \"%s\"}", sender);

    return resultado;
}

char *crearJson_user_info(const char *sender, const char *target)
{
    int tamaño = snprintf(NULL, 0,
                          "{\"type\": \"user_info\", \"sender\": \"%s\", \"target\": \"%s\"}", sender, target) +
                 1;

    char *resultado = (char *)malloc(tamaño);
    if (!resultado)
        return NULL;

    snprintf(resultado, tamaño,
             "{\"type\": \"user_info\", \"sender\": \"%s\", \"target\": \"%s\"}", sender, target);

    return resultado;
}

char *crearJson_change_status(const char *sender, const char *nuevo_estado)
{
    int tamaño = snprintf(NULL, 0,
                          "{\"type\": \"change_status\", \"sender\": \"%s\", \"content\": \"%s\"}",
                          sender, nuevo_estado) +
                 1;

    char *resultado = (char *)malloc(tamaño);
    if (!resultado)
        return NULL;

    snprintf(resultado, tamaño,
             "{\"type\": \"change_status\", \"sender\": \"%s\", \"content\": \"%s\"}",
             sender, nuevo_estado);

    return resultado;
}

char *crearJson_disconnect(const char *sender)
{
    int tamaño = snprintf(NULL, 0,
                          "{\"type\": \"disconnect\", \"sender\": \"%s\", \"content\": \"Cierre de sesi\u00f3n\"}",
                          sender) +
                 1;

    char *resultado = (char *)malloc(tamaño);
    if (!resultado)
        return NULL;

    snprintf(resultado, tamaño,
             "{\"type\": \"disconnect\", \"sender\": \"%s\", \"content\": \"Cierre de sesi\u00f3n\"}",
             sender);

    return resultado;
}

// int main() {
//     const char* nombre = "paolo";
//     const char* valor = "123";

//     // Crear el string JSON
//     char* json = crearJson_register(nombre);

//     // Imprimir el resultado
//     if (json) {
//         printf("%s\n", json);
//         free(json);  // Liberar la memoria
//     }

//     return 0;
// }

// int main() {

//     const char *input_string = "{ \"nombre\": \"Jose\", \"edad\": 25 }fasdfasdf";
//     char extracted_json[256];

//     extract_json(input_string, extracted_json);

//     const char *json = extracted_json;
//     JsonPair pairs[10];

//     int num_pairs = parse_json(json, pairs, 10);
//     if (num_pairs < 0) {
//         printf("Error al parsear JSON\n");
//         return 1;
//     }

//     for (int i = 0; i < num_pairs; i++) {
//         if (pairs[i].isNumber) {
//             printf("%s: %d\n", pairs[i].key, atoi(pairs[i].value));
//         } else {
//             printf("%s: %s\n", pairs[i].key, pairs[i].value);
//         }
//     }

//     JsonPair pair[] = {
//         {"nombre", "Martin"},
//     };

//     char json_output[256];
//     create_json(pair, 3, json_output, sizeof(json_output));

//     printf("JSON generado: %s\n", json_output);

//     return 0;
// }
