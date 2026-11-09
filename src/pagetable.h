#ifndef PAGETABLE_H
#define PAGETABLE_H

#include <stddef.h>

typedef enum {
    TABELA_DENSA,
    TABELA_HIER2,
    TABELA_HIER3,
    TABELA_INVERTIDA
} TipoTabela;

typedef struct TabelaPaginas TabelaPaginas;

TabelaPaginas *tabela_criar(TipoTabela tipo, unsigned int bits_vpn, int num_quadros);
int tabela_buscar(TabelaPaginas *tabela, unsigned int vpn);
void tabela_mapear(TabelaPaginas *tabela, unsigned int vpn, int frame_id);
void tabela_desmapear(TabelaPaginas *tabela, unsigned int vpn);
void tabela_destruir(TabelaPaginas *tabela);
size_t tabela_memoria_usada(TabelaPaginas *tabela);

#endif
