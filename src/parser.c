#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

typedef struct {
    char key[50];
    char value[50];
    int isNumber;
} JsonPair;

void remove_spaces(char *str) {
    char *i = str, *j = str;
    while (*i != '\0') {
        if (!isspace((unsigned char)*i)) {
            *j++ = *i;
        }
        i++;
    }
    *j = '\0';
}

int parse_json(const char *json_str, JsonPair *pairs, int max_pairs) {
    char buffer[256];
    strncpy(buffer, json_str, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    remove_spaces(buffer);

    if (buffer[0] != '{' || buffer[strlen(buffer) - 1] != '}') {
        return -1; // JSON inválido
    }

    int count = 0;
    char *token = strtok(buffer + 1, ",}");
    while (token && count < max_pairs) {
        char *colon = strchr(token, ':');
        if (!colon) return -1; // JSON inválido

        *colon = '\0';
        strncpy(pairs[count].key, token + 1, strlen(token) - 2);
        pairs[count].key[strlen(token) - 2] = '\0';

        char *value = colon + 1;
        if (value[0] == '\"') {  // String
            strncpy(pairs[count].value, value + 1, strlen(value) - 2);
            pairs[count].value[strlen(value) - 2] = '\0';
            pairs[count].isNumber = 0;
        } else {  // Número
            strncpy(pairs[count].value, value, sizeof(pairs[count].value) - 1);
            pairs[count].isNumber = 1;
        }

        count++;
        token = strtok(NULL, ",}");
    }

    return count;
}

int main() {
    const char *json = "{ \"nombre\": \"Jose\", \"edad\": 25 }";
    JsonPair pairs[10];

    int num_pairs = parse_json(json, pairs, 10);
    if (num_pairs < 0) {
        printf("Error al parsear JSON\n");
        return 1;
    }

    for (int i = 0; i < num_pairs; i++) {
        if (pairs[i].isNumber) {
            printf("%s: %d\n", pairs[i].key, atoi(pairs[i].value));
        } else {
            printf("%s: %s\n", pairs[i].key, pairs[i].value);
        }
    }

    return 0;
}
