#include "algoritmos.h"
#include <stdlib.h>
/*
 * 
 * Cada função abaixo deve retornar o índice do quadro físico que será
 * substituído (a "vítima"), isto é, um inteiro no intervalo [0, mmu->num_quadros - 1].
 *
 * Campos úteis disponíveis em cada quadro (mmu->quadros[i]):
 *   - mmu->quadros[i].vpn           : Número da página virtual atualmente mapeada
 *   - mmu->quadros[i].ref           : Bit de referência (1 se acessado recentemente, 0 caso contrário)
 *   - mmu->quadros[i].dirty         : Bit de modificação (1 se sofreu escrita, 0 se apenas leitura)
 *   - mmu->quadros[i].ultimo_acesso : Timestamp lógico do último acesso (usado por LRU)
 *   - mmu->quadros[i].tempo_carga   : Timestamp lógico de quando a página foi carregada (usado por FIFO)
 *
 * Campos úteis na MMU (mmu):
 *   - mmu->num_quadros              : Quantidade total de quadros físicos na memória
 *   - mmu->ponteiro_clock           : Índice circular para o algoritmo CLOCK
 *   - mmu->ponteiro_fifo            : Índice circular / fila para o algoritmo FIFO
 *   - mmu->total_acessos            : Contador global de acessos à memória
 */


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


  //Politica CLOCK:
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


// Politica FIFO (First In, First Out):
int fifo_substituir(MMU *mmu) {
    int fifo = mmu->ponteiro_fifo;
    mmu->ponteiro_fifo = (mmu->ponteiro_fifo + 1) % mmu->num_quadros;
    return fifo;
}
