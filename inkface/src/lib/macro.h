#define LOG(...) \
    fprintf(stderr,"[%s:%d] ",__FILE__,__LINE__); \
    fprintf(stderr,__VA_ARGS__); \
    fprintf(stderr,"\n"); 

#define ASSERT(x) \
        if (!(x)) { \
           printf("Assertion failed: %s:%d <<%s>>\n", \
                __FILE__,__LINE__,__FUNCTION__); \
           exit(1); \
        }

