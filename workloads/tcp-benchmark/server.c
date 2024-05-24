/* 
 * Attention:
 * To keep things simple, do not handle socket/bind/listen/.../epoll_create/epoll_wait API error 
 */
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <arpa/inet.h>

#define DEFAULT_PORT    5569
#define MAX_CONN        60
#define MAX_EVENTS      100000
#define BUF_SIZE        16
#define MAX_LINE        256
#define MAX 3000
#define DATA "VKX,"
#define INPUT_LENGTH 4

void server_run();
void client_run();

int main(int argc, char *argv[])
{
	int opt;
	char role = 's';
	while ((opt = getopt(argc, argv, "cs")) != -1) {
		switch (opt) {
		case 'c':
			role = 'c';
			break;
		case 's':
			break;
		default:
			printf("usage: %s [-cs]\n", argv[0]);
			exit(1);
		}
	}
	if (role == 's') {
		server_run();
	} else {
		client_run();
	}
	return 0;
}

/*
 * register events of fd to epfd
 */
static void epoll_ctl_add(int epfd, int fd, uint32_t events)
{
	struct epoll_event ev;
	ev.events = events;
	ev.data.fd = fd;
	if (epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev) == -1) {
		perror("epoll_ctl()\n");
		exit(1);
	}
}

static void set_sockaddr(struct sockaddr_in *addr)
{
    //char *ip = "127.0.0.1";
	bzero((char *)addr, sizeof(struct sockaddr_in));
	addr->sin_family = AF_INET;
	addr->sin_addr.s_addr = INADDR_ANY;
	addr->sin_port = htons(DEFAULT_PORT);
}

static int setnonblocking(int sockfd)
{
	if (fcntl(sockfd, F_SETFL, fcntl(sockfd, F_GETFL, 0) | O_NONBLOCK) ==
	    -1) {
		return -1;
	}
	return 0;
}

/*
 * epoll echo server
 */
void server_run()
{
	int connections;
    int size;
	int i;
	int n;
	int epfd;
	int nfds;
	int listen_sock;
	int conn_sock;
	int socklen;
	char buf[MAX];
	struct sockaddr_in srv_addr;
	struct sockaddr_in cli_addr;
	struct epoll_event events[MAX_EVENTS];

	listen_sock = socket(AF_INET, SOCK_STREAM, 0);

	set_sockaddr(&srv_addr);
	bind(listen_sock, (struct sockaddr *)&srv_addr, sizeof(srv_addr));

	setnonblocking(listen_sock);
	listen(listen_sock, MAX_CONN);

	epfd = epoll_create(1);
	epoll_ctl_add(epfd, listen_sock, EPOLLIN | EPOLLOUT | EPOLLET);

	socklen = sizeof(cli_addr);
    fprintf(stdout, "Listening...\n");
	for (;;) {
		nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);
		for (i = 0; i < nfds; i++) {
			if (events[i].data.fd == listen_sock) {
				/* handle new connection */
				fprintf(stdout, "New connection\n");
				conn_sock =
				    accept(listen_sock,
					   (struct sockaddr *)&cli_addr,
					   &socklen);
				
				fprintf(stdout, "Accepted connection\n");

				inet_ntop(AF_INET, (char *)&(cli_addr.sin_addr),
					  buf, sizeof(cli_addr));
				fprintf(stdout,"[+] connected with %s:%d\n", buf,
				       ntohs(cli_addr.sin_port));

				setnonblocking(conn_sock);
				epoll_ctl_add(epfd, conn_sock,
					      EPOLLIN | EPOLLET | EPOLLRDHUP |
					      EPOLLHUP);
				
				connections++;
			} else if (events[i].events & EPOLLIN) {
				/* handle EPOLLIN event */
				for (;;) {
					bzero(buf, sizeof(buf));
					n = read(events[i].data.fd, buf,
						 sizeof(buf));
					if (n <= 0 /* || errno == EAGAIN */ ) {
						break;
                    } else if (n < INPUT_LENGTH) {
                        fprintf(stdout, "Stopped reading earlier than expected\n");
                        break;
					} else {
					    // Parse integer from buffer
                        size = atoi(buf);

                        for (int i = 0; i < size*4; i+=4)
                        {
							memcpy(buf+i, DATA, 4);
                        }
        
                        // Send the buffer to client - BLOCKING
                        write(events[i].data.fd, buf, size*4);
					}
				}
			} else {
				fprintf(stderr, "[+] unexpected\n");
			}
			/* check if the connection is closing */
			if (events[i].events & (EPOLLRDHUP | EPOLLHUP)) {
				fprintf(stdout, "[+] connection closed\n");
				epoll_ctl(epfd, EPOLL_CTL_DEL,
					  events[i].data.fd, NULL);
				close(events[i].data.fd);
				connections--;
				continue;
			}
		}

		if(connections==0){
			break;
		}
	}
}

/*
 * test clinet 
 */
void client_run()
{
	int n;
	int c;
	int sockfd;
	char buf[MAX_LINE];
	struct sockaddr_in srv_addr;

	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	set_sockaddr(&srv_addr);

	if (connect(sockfd, (struct sockaddr *)&srv_addr, sizeof(srv_addr)) < 0) {
		perror("connect()");
		exit(1);
	}

	for (;;) {
		printf("input: ");
		fgets(buf, sizeof(buf), stdin);
		c = strlen(buf) - 1;
		buf[c] = '\0';
		write(sockfd, buf, c + 1);

		bzero(buf, sizeof(buf));
		while (errno != EAGAIN
		       && (n = read(sockfd, buf, sizeof(buf))) > 0) {
			printf("echo: %s\n", buf);
			bzero(buf, sizeof(buf));

			c -= n;
			if (c <= 0) {
				break;
			}
		}
	}
	close(sockfd);
}