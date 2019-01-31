objects = aux1.o aux2.o

compile: $(objects)
	gcc -Wall -O3 -o main $(objects) main.c
	rm $(objects)

run: compile
	./main

aux1.o: includes/aux1.c
	gcc -c -Wall -O3 includes/aux1.c

aux2.o: includes/aux2.c
	gcc -c -Wall -O3 includes/aux2.c

clean: 
	rm -f $(objects) main

