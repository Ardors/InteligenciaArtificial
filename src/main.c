/*
 * main.c
 *
 * This source herein may be modified and/or distributed by anybody who
 * so desires, with the following restrictions:
 *    1.)  No portion of this notice shall be removed.
 *    2.)  Credit shall not be taken for the creation of this source.
 *    3.)  This code is not to be traded, sold, or used for personal
 *         gain or profit.
 *
 */

#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include "rogue.h"
#include "init.h"
#include "level.h"
#include "main.h"
#include "message.h"
#include "monster.h"
#include "object.h"
#include "play.h"
#include "trap.h"
#include "socket_client.h"

extern short party_room;
extern object level_objects;
extern object level_monsters;

const int PORT = 2300;
const char* SERVERNAME = "localhost";
#define BUFFSIZE sizeof(payload)
char buff[BUFFSIZE];
int sock;
int nread;
time_t t;

int saved_uid;
int true_uid;

void turn_into_games(void)
{
	if(setuid(saved_uid) == -1)
	{
		perror("setuid restore failed!");
		clean_up("");
	}
}

void turn_into_user(void)
{
	if(setuid(true_uid)==-1)
	{
		perror("setuid(restore)");
		clean_up("");
	}
}

int main(int argc, char *argv[])
{
	/* Save the setuid we have got, then turn back into the player */
	saved_uid = geteuid();
	setuid(true_uid = getuid());

	if (init(argc, argv))	/* restored game */
	{
		goto PL;
	}

	for (;;)
	{
		clear_level();
		make_level();
		put_objects();
		put_stairs();
		add_traps();
		put_mons();
		put_player(party_room);
		print_stats(STAT_ALL);
PL:		
		srand((unsigned) time(&t));
		
		struct sockaddr_in server_address;
		memset(&server_address, 0, sizeof(server_address));
		server_address.sin_family = AF_INET;
		inet_pton(AF_INET, SERVERNAME, &server_address.sin_addr);
		server_address.sin_port = htons(PORT);

		if ((sock = socket(PF_INET, SOCK_STREAM, 0)) < 0) {
			printf("ERROR: Socket creation failed\n");
			return 1;
		}

		if (connect(sock, (struct sockaddr*)&server_address, sizeof(server_address)) < 0) {
			printf("ERROR: Unable to connect to server\n");
			return 1;
		}
		
		play_level();
		free_stuff(&level_objects);
		free_stuff(&level_monsters);
	}

	return 0;
}
