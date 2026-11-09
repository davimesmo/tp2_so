#ifndef ALGORITMOS_H
#define ALGORITMOS_H

#include "mmu.h"

int random_substituir(MMU *mmu);
int lru_substituir(MMU *mmu);
int clock_substituir(MMU *mmu);
int fifo_substituir(MMU *mmu);

#endif
