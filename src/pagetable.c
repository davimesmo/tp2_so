#include "pagetable.h"
#include <stdlib.h>
#include <string.h>

typedef struct {
    unsigned int vpn;
    int next;
} InvertidaNode;

struct TabelaPaginas {
    TipoTabela tipo;
    unsigned int bits_vpn;
    int num_quadros;
    size_t memoria_usada;

    int *densa_entradas;

    int **h2_l1;
    unsigned int h2_bits_l1;
    unsigned int h2_bits_l2;

    int ***h3_l1;
    unsigned int h3_bits_l1;
    unsigned int h3_bits_l2;
    unsigned int h3_bits_l3;

    int *inv_hash_head;
    InvertidaNode *inv_frames;
};

static unsigned int hash_vpn(unsigned int vpn, int num_quadros) {
    return (vpn * 2654435761U) % (unsigned int)num_quadros;
}

TabelaPaginas *tabela_criar(TipoTabela tipo, unsigned int bits_vpn, int num_quadros) {
    TabelaPaginas *t = (TabelaPaginas *)calloc(1, sizeof(TabelaPaginas));
    if (!t) return NULL;

    t->tipo = tipo;
    t->bits_vpn = bits_vpn;
    t->num_quadros = num_quadros;
    t->memoria_usada = sizeof(TabelaPaginas);

    if (tipo == TABELA_DENSA) {
        size_t qtd = (size_t)1 << bits_vpn;
        t->densa_entradas = (int *)malloc(qtd * sizeof(int));
        for (size_t i = 0; i < qtd; i++) {
            t->densa_entradas[i] = -1;
        }
        t->memoria_usada += qtd * sizeof(int);
    } 
    else if (tipo == TABELA_HIER2) {
        t->h2_bits_l1 = bits_vpn / 2;
        t->h2_bits_l2 = bits_vpn - t->h2_bits_l1;

        size_t qtd_l1 = (size_t)1 << t->h2_bits_l1;
        t->h2_l1 = (int **)calloc(qtd_l1, sizeof(int *));
        t->memoria_usada += qtd_l1 * sizeof(int *);
    } 
    else if (tipo == TABELA_HIER3) {
        t->h3_bits_l1 = bits_vpn / 3;
        t->h3_bits_l2 = bits_vpn / 3;
        t->h3_bits_l3 = bits_vpn - t->h3_bits_l1 - t->h3_bits_l2;

        size_t qtd_l1 = (size_t)1 << t->h3_bits_l1;
        t->h3_l1 = (int ***)calloc(qtd_l1, sizeof(int **));
        t->memoria_usada += qtd_l1 * sizeof(int **);
    } 
    else if (tipo == TABELA_INVERTIDA) {
        t->inv_hash_head = (int *)malloc(num_quadros * sizeof(int));
        t->inv_frames = (InvertidaNode *)malloc(num_quadros * sizeof(InvertidaNode));

        for (int i = 0; i < num_quadros; i++) {
            t->inv_hash_head[i] = -1;
            t->inv_frames[i].vpn = 0;
            t->inv_frames[i].next = -1;
        }
        t->memoria_usada += num_quadros * sizeof(int) + num_quadros * sizeof(InvertidaNode);
    }

    return t;
}

int tabela_buscar(TabelaPaginas *tabela, unsigned int vpn) {
    if (!tabela) return -1;

    if (tabela->tipo == TABELA_DENSA) {
        return tabela->densa_entradas[vpn];
    }

    if (tabela->tipo == TABELA_HIER2) {
        unsigned int idx1 = vpn >> tabela->h2_bits_l2;
        unsigned int idx2 = vpn & (((unsigned int)1 << tabela->h2_bits_l2) - 1);

        if (!tabela->h2_l1[idx1]) return -1;
        return tabela->h2_l1[idx1][idx2];
    }

    if (tabela->tipo == TABELA_HIER3) {
        unsigned int shift2 = tabela->h3_bits_l2 + tabela->h3_bits_l3;
        unsigned int idx1 = vpn >> shift2;
        unsigned int idx2 = (vpn >> tabela->h3_bits_l3) & (((unsigned int)1 << tabela->h3_bits_l2) - 1);
        unsigned int idx3 = vpn & (((unsigned int)1 << tabela->h3_bits_l3) - 1);

        if (!tabela->h3_l1[idx1]) return -1;
        if (!tabela->h3_l1[idx1][idx2]) return -1;
        return tabela->h3_l1[idx1][idx2][idx3];
    }

    if (tabela->tipo == TABELA_INVERTIDA) {
        unsigned int h = hash_vpn(vpn, tabela->num_quadros);
        int curr = tabela->inv_hash_head[h];
        while (curr != -1) {
            if (tabela->inv_frames[curr].vpn == vpn) {
                return curr;
            }
            curr = tabela->inv_frames[curr].next;
        }
        return -1;
    }

    return -1;
}

void tabela_mapear(TabelaPaginas *tabela, unsigned int vpn, int frame_id) {
    if (!tabela) return;

    if (tabela->tipo == TABELA_DENSA) {
        tabela->densa_entradas[vpn] = frame_id;
    } 
    else if (tabela->tipo == TABELA_HIER2) {
        unsigned int idx1 = vpn >> tabela->h2_bits_l2;
        unsigned int idx2 = vpn & (((unsigned int)1 << tabela->h2_bits_l2) - 1);

        if (!tabela->h2_l1[idx1]) {
            size_t qtd_l2 = (size_t)1 << tabela->h2_bits_l2;
            tabela->h2_l1[idx1] = (int *)malloc(qtd_l2 * sizeof(int));
            for (size_t i = 0; i < qtd_l2; i++) {
                tabela->h2_l1[idx1][i] = -1;
            }
            tabela->memoria_usada += qtd_l2 * sizeof(int);
        }
        tabela->h2_l1[idx1][idx2] = frame_id;
    } 
    else if (tabela->tipo == TABELA_HIER3) {
        unsigned int shift2 = tabela->h3_bits_l2 + tabela->h3_bits_l3;
        unsigned int idx1 = vpn >> shift2;
        unsigned int idx2 = (vpn >> tabela->h3_bits_l3) & (((unsigned int)1 << tabela->h3_bits_l2) - 1);
        unsigned int idx3 = vpn & (((unsigned int)1 << tabela->h3_bits_l3) - 1);

        if (!tabela->h3_l1[idx1]) {
            size_t qtd_l2 = (size_t)1 << tabela->h3_bits_l2;
            tabela->h3_l1[idx1] = (int **)calloc(qtd_l2, sizeof(int *));
            tabela->memoria_usada += qtd_l2 * sizeof(int *);
        }

        if (!tabela->h3_l1[idx1][idx2]) {
            size_t qtd_l3 = (size_t)1 << tabela->h3_bits_l3;
            tabela->h3_l1[idx1][idx2] = (int *)malloc(qtd_l3 * sizeof(int));
            for (size_t i = 0; i < qtd_l3; i++) {
                tabela->h3_l1[idx1][idx2][i] = -1;
            }
            tabela->memoria_usada += qtd_l3 * sizeof(int);
        }

        tabela->h3_l1[idx1][idx2][idx3] = frame_id;
    } 
    else if (tabela->tipo == TABELA_INVERTIDA) {
        unsigned int h = hash_vpn(vpn, tabela->num_quadros);
        tabela->inv_frames[frame_id].vpn = vpn;
        tabela->inv_frames[frame_id].next = tabela->inv_hash_head[h];
        tabela->inv_hash_head[h] = frame_id;
    }
}

void tabela_desmapear(TabelaPaginas *tabela, unsigned int vpn) {
    if (!tabela) return;

    if (tabela->tipo == TABELA_DENSA) {
        tabela->densa_entradas[vpn] = -1;
    } 
    else if (tabela->tipo == TABELA_HIER2) {
        unsigned int idx1 = vpn >> tabela->h2_bits_l2;
        unsigned int idx2 = vpn & (((unsigned int)1 << tabela->h2_bits_l2) - 1);
        if (tabela->h2_l1[idx1]) {
            tabela->h2_l1[idx1][idx2] = -1;
        }
    } 
    else if (tabela->tipo == TABELA_HIER3) {
        unsigned int shift2 = tabela->h3_bits_l2 + tabela->h3_bits_l3;
        unsigned int idx1 = vpn >> shift2;
        unsigned int idx2 = (vpn >> tabela->h3_bits_l3) & (((unsigned int)1 << tabela->h3_bits_l2) - 1);
        unsigned int idx3 = vpn & (((unsigned int)1 << tabela->h3_bits_l3) - 1);
        if (tabela->h3_l1[idx1] && tabela->h3_l1[idx1][idx2]) {
            tabela->h3_l1[idx1][idx2][idx3] = -1;
        }
    } 
    else if (tabela->tipo == TABELA_INVERTIDA) {
        unsigned int h = hash_vpn(vpn, tabela->num_quadros);
        int curr = tabela->inv_hash_head[h];
        int prev = -1;

        while (curr != -1) {
            if (tabela->inv_frames[curr].vpn == vpn) {
                if (prev == -1) {
                    tabela->inv_hash_head[h] = tabela->inv_frames[curr].next;
                } else {
                    tabela->inv_frames[prev].next = tabela->inv_frames[curr].next;
                }
                tabela->inv_frames[curr].next = -1;
                break;
            }
            prev = curr;
            curr = tabela->inv_frames[curr].next;
        }
    }
}

void tabela_destruir(TabelaPaginas *tabela) {
    if (!tabela) return;

    if (tabela->tipo == TABELA_DENSA) {
        free(tabela->densa_entradas);
    } 
    else if (tabela->tipo == TABELA_HIER2) {
        size_t qtd_l1 = (size_t)1 << tabela->h2_bits_l1;
        for (size_t i = 0; i < qtd_l1; i++) {
            if (tabela->h2_l1[i]) {
                free(tabela->h2_l1[i]);
            }
        }
        free(tabela->h2_l1);
    } 
    else if (tabela->tipo == TABELA_HIER3) {
        size_t qtd_l1 = (size_t)1 << tabela->h3_bits_l1;
        size_t qtd_l2 = (size_t)1 << tabela->h3_bits_l2;
        for (size_t i = 0; i < qtd_l1; i++) {
            if (tabela->h3_l1[i]) {
                for (size_t j = 0; j < qtd_l2; j++) {
                    if (tabela->h3_l1[i][j]) {
                        free(tabela->h3_l1[i][j]);
                    }
                }
                free(tabela->h3_l1[i]);
            }
        }
        free(tabela->h3_l1);
    } 
    else if (tabela->tipo == TABELA_INVERTIDA) {
        free(tabela->inv_hash_head);
        free(tabela->inv_frames);
    }

    free(tabela);
}

size_t tabela_memoria_usada(TabelaPaginas *tabela) {
    if (!tabela) return 0;
    return tabela->memoria_usada;
}
