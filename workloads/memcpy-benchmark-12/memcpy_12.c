#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX 3000
#define SIZE 1024 * 1024 * 1024 * 12UL
#define CALLS 1048576
#define REPETITIONS 8


void copy_single_memcpy(){
    char *origin;
    char *dest;

    origin = (char *) malloc(SIZE);
    dest = (char *) malloc(SIZE);

    memcpy(dest, origin, SIZE);

    free(origin);
    free(dest);
}

void copy_multi_memcpy(){
    char *origin;
    char *dest;

    origin = (char *) malloc(SIZE);
    dest = (char *) malloc(SIZE);

    int threads = 8;
    long chunk_size = SIZE / threads;

    pid_t child_pid, wpid;
    int status = 0;

    for (int i = 0; i < threads; i++)
    {
        child_pid = fork();
        if (child_pid == 0)
        {
            memcpy(dest + i * chunk_size, origin + i * chunk_size, chunk_size);
            exit(0);
        }
    }

    while ((wpid = wait(&status)) > 0);

    free(origin);
    free(dest);
}

void copy_multiple_calls(){
    char *origin;
    char *dest;

    origin = (char *) malloc(SIZE);
    dest = (char *) malloc(SIZE);

    long chunk_size = SIZE / CALLS;

    for (long i = 0; i < CALLS; i++)
    {
        memcpy(dest + i * chunk_size, origin + i * chunk_size, chunk_size);
    }

    free(origin);
    free(dest);
}

int main(int argc, char *argv[])
{

    for(int i = 0; i < REPETITIONS; i++){
        copy_single_memcpy();
    }

    printf("Finished %d copies of 12 GB in 1 call\n", REPETITIONS);
    fflush(stdout);

    for(int i = 0; i < REPETITIONS; i++){
        copy_multi_memcpy();
    }
    printf("Finished %d copies of 12 GB in 8 threads\n", REPETITIONS);
    fflush(stdout);

    for(int i = 0; i < REPETITIONS; i++){
        copy_multiple_calls();
    }
    printf("Finished %d copies of 12 GB in %d calls\n", REPETITIONS, CALLS);
    fflush(stdout);

    return 0;
}
