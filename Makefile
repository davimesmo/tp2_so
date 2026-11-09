CC = gcc
CFLAGS = -Wall -Wextra -O3 -std=c99 -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE
SRC = src/main.c src/mmu.c src/pagetable.c src/algoritmos.c
OBJ = $(SRC:.c=.o)
TARGET = simulador

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ)
	ln -sf $(TARGET) tp2virtual

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET) tp2virtual

.PHONY: all clean
