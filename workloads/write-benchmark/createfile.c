#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/timeb.h>

#define BUFFERSIZE (64*1024)
#define MEGABYTE (1024*1024)

/* Takes two arguments.  Arg 1 is file name.
arg 2 is number of megabytes to write. */

main(int argc, char * argv[])
{
long megabytes,j,i;
int outputfile;
char buffer[BUFFERSIZE];
struct timeb before,after;

if (argc !=3)
    {
    printf("Arguments are filename to create and size in megabytes\n");
    return -1;
    }

for (j=0 ; j < BUFFERSIZE ;j++)
    buffer[j]='X';

outputfile = open(argv[1], O_CREAT | O_WRONLY | O_SYNC);
megabytes=atol(argv[2]);

ftime(&before);

for (i=0 ; i<((MEGABYTE/BUFFERSIZE)*megabytes) ; i++)
   write(outputfile,buffer,BUFFERSIZE);

ftime(&after);

long timetowrite=after.time-before.time;

if (timetowrite > 0)
printf("Bytes per second written = %d\n",
    (MEGABYTE*megabytes)/timetowrite);

close(outputfile);

return 0;
}

