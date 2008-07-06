LIBS=`pkg-config --libs cairo librsvg-2.0 libxml-2.0 `
INCS=`pkg-config --cflags cairo librsvg-2.0 libxml-2.0 ` 

.c.o:
	$(CC) -g -Wall $(CFLAGS) $(INCS) -I. -c $*.c

all: inkfun 

inkfun: inkfun.o
	$(CC) -g -Wall $(CFLAGS) -o $@ inkfun.o $(LIBS)

clean:
	rm -rf *.o inkfun 

