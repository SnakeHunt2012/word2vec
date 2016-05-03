#include <stdio.h>
#include <string.h>

#define MAX 1024

long long BKDRHash(char *str)
{
    long long hash = 0, seed = 131313; // 31 131 1313 13131 131313 etc..
    int i, length = strlen(str);
    
    for(i = 0; i < length; i++)
        hash = (hash * seed) + str[i];
    return hash;
}

int main(int argc, char *argv[])
{
    char line[MAX];
    FILE *fin = fopen(argv[1], "r");

    while (fgets(line, MAX, fin) != NULL && strlen(line))
        printf("%010d\t%s", BKDRHash(line), line);
    return 0;
}
