#ifndef MMU_H
#define MMU_H

#include "pagetable.h"

typedef struct {
    unsigned int vpn;
    int ocupado;
    int dirty;
    int ref;
    unsigned long ultimo_acesso;
    unsigned long tempo_carga;
} Quadro;

typedef struct {
    Quadro *quadros;
    int num_quadros;
    int quadros_ocupados;
    unsigned int tam_pagina_kb;
    unsigned int tam_memoria_kb;
    unsigned int shift_s;
    unsigned long total_acessos;
    unsigned long paginas_lidas;
    unsigned long paginas_escritas;
    TabelaPaginas *tabela;
    char algoritmo[32];
    int ponteiro_clock;
    int ponteiro_fifo;
} MMU;

MMU *mmu_criar(const char *algoritmo, unsigned int tam_pagina_kb, unsigned int tam_memoria_kb, TipoTabela tipo_tabela);
void mmu_processar_acesso(MMU *mmu, unsigned int addr, char rw);
void mmu_destruir(MMU *mmu);

#endif
