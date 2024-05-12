#include <stdio.h>     // for fprintf()
#include <unistd.h>    // for close()
#include <sys/epoll.h> // for epoll_create1(), epoll_ctl(), struct epoll_event
	
int main()
{
	struct epoll_event event, events[3];
	int epoll_fd = epoll_create1(0);
	
	if (epoll_fd == -1) {
		fprintf(stderr, "Failed to create epoll file descriptor\n");
		return 1;
	}
	
	event.events = EPOLLIN;
	event.data.fd = 0;

    epoll_wait(epoll_fd, events, 1, 120000);
	
	if (close(epoll_fd)) {
		fprintf(stderr, "Failed to close epoll file descriptor\n");
		return 1;
	}
	return 0;

}