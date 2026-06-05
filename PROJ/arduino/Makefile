# generic flags
CC=avr-gcc
CPPFLAGS=-DF_CPU=16000000UL
CFLAGS=-Wall -std=c99 -O3 -mmcu=atmega328p -fshort-enums 
LDFLAGS=-std=c99 -mmcu=atmega328p -flto

# flags to use printf with floats (see README.org)
CPRINTFLAGS=-Wl,-u,vfprintf
LDPRINTFLAGS=-lprintf_flt -lm
CFLAGS+=$(CPRINTFLAGS)
LDFLAGS+=$(LDPRINTFLAGS)

# joining flags
FLAGS=$(CFLAGS) $(CPPFLAGS) $(LDFLAGS)

# target device
DEVICE=/dev/ttyACM0

# sources
SRC_c:=$(wildcard *.c)
SRC:=$(wildcard *.c *.h)
SRC+=Makefile

# directives
.PHONY : all load_% picocom veryclean clean touch 

all: load_main size clean picocom

%.s: %.c
	$(CC) $(CFLAGS) -S $<

main: $(SRC)
	$(CC) $(FLAGS) $(SRC_c) -o main

%.hex: %
	avr-objcopy -Oihex $< $@

load_%: %.hex
	avrdude -c arduino -p atmega328p -P $(DEVICE) -U $<

clean:
	rm -f *~ *.hex *.s *.o main

