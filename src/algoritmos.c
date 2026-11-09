#include "algoritmos.h"
#include <stdlib.h>

/* Aluno 1: Politica Random */
int random_substituir(MMU *mmu) {
    return (int)(random() % mmu->num_quadros);
}

/* Aluno 1: Politica LRU */
int lru_substituir(MMU *mmu) {
    int vitima = 0;
    unsigned long menor_tempo = mmu->quadros[0].ultimo_acesso;

    for (int i = 1; i < mmu->num_quadros; i++) {
        if (mmu->quadros[i].ultimo_acesso < menor_tempo) {
            menor_tempo = mmu->quadros[i].ultimo_acesso;
            vitima = i;
        }
    }
    return vitima;
}

/* Aluno 2: Politica CLOCK */
int clock_substituir(MMU *mmu) {
    while (1) {
        int idx = mmu->ponteiro_clock;
        mmu->ponteiro_clock = (mmu->ponteiro_clock + 1) % mmu->num_quadros;

        if (mmu->quadros[idx].ref == 0) {
            return idx;
        }
        mmu->quadros[idx].ref = 0;
    }
}

/* Aluno 2: Politica FIFO */
int fifo_substituir(MMU *mmu) {
    int vitima = 0;
    unsigned long menor_tempo = mmu->quadros[0].tempo_carga;

    for (int i = 1; i < mmu->num_quadros; i++) {
        if (mmu->quadros[i].tempo_carga < menor_tempo) {
            menor_tempo = mmu->quadros[i].tempo_carga;
            vitima = i;
        }
    }
    return vitima;
}
