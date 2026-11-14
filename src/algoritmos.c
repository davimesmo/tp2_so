#include "algoritmos.h"
#include <stdlib.h>

// Politica Random
int random_substituir(MMU *mmu) {
    return random() % mmu->num_quadros;
}

// Politica LRU
int lru_substituir(MMU *mmu) {
    int lru = 0;
    unsigned long int lru_timestamp = mmu->quadros[lru].ultimo_acesso;

    for (int i=1; i < mmu->num_quadros; i++){
        if (mmu->quadros[i].ultimo_acesso < lru_timestamp){
            lru = i;
            lru_timestamp = mmu->quadros[i].ultimo_acesso;
        }
    }

    return lru;
}


 //Politica CLOCK
int clock_substituir(MMU *mmu) {
    int clock = 0;
    while( 1 == 1){
        if( mmu->quadros[mmu->ponteiro_clock].ref == 0){
            clock = mmu->ponteiro_clock;
            mmu->ponteiro_clock = (mmu->ponteiro_clock + 1) % mmu->num_quadros;
            break;
        }else{
            mmu->quadros[mmu->ponteiro_clock].ref = 0;
            mmu->ponteiro_clock = (mmu->ponteiro_clock + 1) % mmu->num_quadros;
        }
        
    }
    return clock;
}


// Politica FIFO
int fifo_substituir(MMU *mmu) {
    int fifo = mmu->ponteiro_fifo;
    mmu->ponteiro_fifo = (mmu->ponteiro_fifo + 1) % mmu->num_quadros;
    return fifo;
}
