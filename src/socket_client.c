/* client.c */

#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <unistd.h>    //write
#include <time.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


void sendMsg(int sock, void* msg, uint32_t msgsize)
{
    if (write(sock, msg, msgsize) < 0)
    {
        printf("Can't send message.\n");
        close(sock);
        exit(1);
    }
    //printf("Message sent (%d bytes).\n", msgsize);
    return;
}
