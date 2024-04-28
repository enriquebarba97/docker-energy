#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>

#define MAX 5000
#define TOTAL_REQUESTS 500000
#define CLIENTS 1
#define DATA "VKX,"

int communication(int connfd, int requests, int list_size, int client_id)
{
    char buffer[MAX];
    char check_buffer[MAX];
    int n, read_bytes, to_read;

    for (int i = 0; i < list_size*4; i++)
    {
        check_buffer[i] = DATA[i % 4];
    }

    printf("[%d] Sending list size %d\n", client_id, list_size);

    for(int i=0;i<requests;i++){
        // Reset buffer
        memset(buffer, '\0', MAX);

        n = 0;
        // while ((buffer[n++] = getchar()) != '\n');

        sprintf(buffer, "%d", list_size);
        write(connfd, buffer, 4);        
        
        read_bytes = 0;
        to_read = list_size*4;

        while (to_read > 0){
            // if(client_id>6){
            //     printf("Client %d waiting for response: %d\n", client_id, to_read);
            // }

            n = read(connfd, buffer + read_bytes, to_read);
            if (n == 0)
            {
                printf("Stopped reading earlier than expected\n");
                printf(buffer);
                break;
            }
            to_read -= n;
            read_bytes += n;
        }

        if (strncmp(check_buffer, buffer, list_size*4) != 0)
        {
            printf("Data mismatch\n");
            return 0;
        }

        if (strncmp("exit", buffer, 4) == 0){
            printf("Server stopping...\n");
            return 0;
        }
    }
    return 1;
}

void benchmark(int connfd, int client_id)
{
    int sizes[] = {100, 300, 500, 600};

    for (int i = 0; i < 4; i++)
    {
        printf("[%d] Benchmarking with list size %d\n", client_id, sizes[i]);
        int result = communication(connfd, TOTAL_REQUESTS/CLIENTS, sizes[i], client_id);
        if (result == 0)
        {
            printf("Server stopped\n");
            return;
        }
        printf("[%d] Benchmarking with list size %d done\n", client_id, sizes[i]);
    }

    return;

}

void run(int myid)
{
    char *ip = "127.0.0.1";
    int port = 5569;

    int sock;
    struct sockaddr_in addr;
    socklen_t addr_size;
    int n;


    sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock < 0){
        printf("[%d] Socket creation failed", myid);
        exit(1);
    }
    printf("[%d] Server socket created\n", myid);

    memset(&addr, '\0', sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = inet_addr(ip);

    if(connect(sock, (struct sockaddr*)&addr, sizeof(addr)) != 0){
        printf("[%d] Connection failed", myid);
        exit(1);
    }

    printf("[%d] Connected to server\n", myid);
    
    benchmark(sock, myid);

    //sleep(1);
    
    close(sock);
    printf("[%d] Connection closed\n", myid);

    return;
}

int main(int argc, char *argv[] ){

    // Parse id from command line
    int myid = atoi(argv[1]);

    printf("[%d] Client started\n", myid);

    run(myid);

    return 0;
}