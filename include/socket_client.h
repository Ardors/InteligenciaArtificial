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
    uint32_t current_exp;
    uint32_t max_exp;
    uint32_t current_strength;
    uint32_t max_strength;
    uint8_t pos_x;
    uint8_t pos_y;
    uint16_t dungeon_level;
    unsigned short map[DROWS][DCOLS];
    int ack;
    uint32_t alive;
    char toBeSent[250];
} payload;

#pragma pack()


void sendMsg(int sock, void* msg, uint32_t msgsize);

