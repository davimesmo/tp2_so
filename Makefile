CC = gcc
CFLAGS = -Wall -Wextra -O3 -std=c99 -Iinclude -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE
SRC = $(wildcard src/*.c)
OBJ = $(patsubst src/%.c, obj/%.o, $(SRC))
TARGET = simulador

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ)
	ln -sf $(TARGET) tp2virtual

obj/%.o: src/%.c | obj
	$(CC) $(CFLAGS) -c $< -o $@

obj:
	mkdir -p obj

clean:
	rm -rf obj $(TARGET) tp2virtual tp2_entrega.tar.gz

pack: clean
	tar -czvf tp2_entrega.tar.gz Makefile src/ include/ tests/ RELATORIO.md

.PHONY: all clean pack
