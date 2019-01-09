#!/bin/bash

if [ ! -f ./main.c ]; then
    exit 0
fi

mkdir -p includes
touch -a makefile

# compile
if ! grep -q "compile:" makefile; then
  printf "compile: \$(objects)\n\tgcc -Wall -O3 -o main \$(objects) main.c\n\trm \$(objects)\n\n" >> makefile
fi

# run
if ! grep -q "run:" makefile; then
  printf "run: compile\n\t./main\n\n" >> makefile
fi

objects=""

for file in ./*; do
    if [[ $file == ./!(main).[ch] ]]; then
        mv $file includes
        sed -i -e 's/[ \t]*#[ \t]*include[ \t]*"'${file:2}'"/#include "includes\/'${file:2}'"/g' main.c
        if [[ $file == ./!(main).[c] ]]; then
            objects=$objects" "${file:2:-2}".o"
            if ! grep -q "${file:2:-2}.o:" makefile; then
              printf "${file:2:-2}.o: includes/${file:2}\n\tgcc -c -Wall -O3 includes/${file:2}\n\n" >> makefile
            fi
        fi
    fi
done

# objects
if grep -q "objects =" makefile
  then
    sed -i -r "s/(objects[ \t]*=.*)/\1$objects/" makefile
  else
    { printf "objects =$objects\n\n"; cat makefile; } > makefile.new
    mv makefile{.new,}
fi

# clean
if ! grep -q "clean:" makefile; then
  printf "clean: \n\trm -f \$(objects) main\n\n" >> makefile
fi
