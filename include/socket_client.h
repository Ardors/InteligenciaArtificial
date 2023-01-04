/* client.c */

#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <unistd.h>    //write
#include <time.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#pragma pack(1)

typedef struct payload_t {
    uint32_t gold;
    uint32_t current_health;
    uint32_t max_health;
} payload;

#pragma pack()


void sendMsg(int sock, void* msg, uint32_t msgsize);

