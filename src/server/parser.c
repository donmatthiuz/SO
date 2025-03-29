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

void remove_spaces(char *str)
{
    char *i = str, *j = str;
    while (*i != '\0')
    {
        if (!isspace((unsigned char)*i))
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
    char *timestamp = get_current_timestamp();
    int tamaño = snprintf(NULL, 0,
                          "{\"type\": \"broadcast\", \"sender\": \"%s\", \"content\": \"%s\", \"timestamp\": \"%s\"}",
                          sender, mensaje, timestamp) +
                 1;

    // Asignar memoria para el mensaje
    char *resultado = (char *)malloc(tamaño);
    if (!resultado)
    {
        free(timestamp); // Liberar timestamp en caso de error
        return NULL;
    }

    // Crear el mensaje con el timestamp
    snprintf(resultado, tamaño,
             "{\"type\": \"broadcast\", \"sender\": \"%s\", \"content\": \"%s\", \"timestamp\": \"%s\"}",
             sender, mensaje, timestamp);

    free(timestamp); // Liberar el timestamp después de usarlo

    return resultado;
}

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