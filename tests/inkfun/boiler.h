
#include <stdio.h>                              

#define BEGIN_MAIN(ARGC,USAGE) \
void usage(void)                                \
{                                               \
    printf("Usage: %s\n",USAGE);                \
}                                               \
                                                \
int main(int argc,char **argv)                  \
{                                               \
    if (argc != 1+ARGC){                        \
        usage();                                \
        exit(1);                                \
    }                                           \


#define END_MAIN \
}

#define ASSERT(x)   \
    if(!(x)) {        \
        printf("Assertion failure: %s:%d <<%s>>\n", \
            __FILE__,__LINE__,__FUNCTION__);        \
    }           
