#include <string.h>
#include <stdio.h>

#define MAX 3000
#define TOTAL_COPIES 4000000
#define DATA "VKX,"



int main(int argc, char *argv[])
{
    cached(100);
    printf("Finished 100 elements from cached\n");
    fflush(stdout);

    cached(300);
    printf("Finished 300 elements from cached\n");
    fflush(stdout);

    cached(500);
    printf("Finished 500 elements from cached\n");
    fflush(stdout);

    cached(600);
    printf("Finished 600 elements from cached\n");
    fflush(stdout);

    from_memory(100);
    printf("Finished 100 elements from memory\n");
    fflush(stdout);


    from_memory(300);
    printf("Finished 300 elements from memory\n");
    fflush(stdout);

    from_memory(500);
    printf("Finished 500 elements from memory\n");
    fflush(stdout);

    from_memory(600);
    printf("Finished 600 elements from memory\n");
    fflush(stdout);
    
    return 0;
}

void cached(int elements){
    char buf[MAX];

    memset(buf, '\0', MAX);

    for(int r=0;r<TOTAL_COPIES;r++){
        for (int i = 0; i < elements*4; i+=4)
        {
            memcpy(buf+i, DATA, 4);
        }
    }
}

void from_memory(int elements){
    char buf[MAX];
    char source[MAX];

    for (int i = 0; i < elements*4; i+=4)
    {
        memcpy(source+i, DATA, 4);
    }

    memset(buf, '\0', MAX);

    for(int r=0;r<TOTAL_COPIES;r++){
        for (int i = 0; i < elements*4; i+=4)
        {
            memcpy(buf+i, source+i, 4);
        }
    }
}