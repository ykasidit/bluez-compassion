# Makefile for bzc_mgmt - use it to call bluez "mgmt" API as described in bluez-src-folder/doc/mgmt-api.txt

#####generic conf
SRC_FILTER = .c
LIBS  = 
CFLAGS = -I.
LDFLAGS =
CONF = .
#SOURCES := $(wildcard ./*${SRC_FILTER} )
SOURCES :=  $(shell find ./ -maxdepth 1 -type f -name '*${SRC_FILTER}')
################

#############config specific conf

ifeq ($(CONF),.)
CFLAGS += -g 
TARGET = bzc_mgmt
CC = gcc
LD = gcc
endif

##################################

OBJS := $(patsubst ./%${SRC_FILTER}, ${CONF}/%.o, $(SOURCES))

all: $(TARGET)

$(TARGET): ${OBJS}
	$(LD) ${OBJS} ${LIBS} ${LDFLAGS} -o ${CONF}/"$(TARGET)"

${CONF}/%.o: %${SRC_FILTER}
	$(CC) $(CFLAGS) -o $@ -c $<

clean:
	rm -f ${CONF}/$(TARGET)
	rm -f $(OBJS)
