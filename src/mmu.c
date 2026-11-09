#include "mmu.h"
#include "algoritmos.h"
#include <stdlib.h>
#include <string.h>
#include <strings.h>

static int selecionar_vitima(MMU *mmu) {
    if (strcasecmp(mmu->algoritmo, "lru") == 0) {
        return lru_substituir(mmu);
    }
    if (strcasecmp(mmu->algoritmo, "random") == 0) {
        return random_substituir(mmu);
    }
    if (strcasecmp(mmu->algoritmo, "clock") == 0) {
        return clock_substituir(mmu);
    }
    if (strcasecmp(mmu->algoritmo, "fifo") == 0) {
        return fifo_substituir(mmu);
    }
    return 0;
}

MMU *mmu_criar(const char *algoritmo, unsigned int tam_pagina_kb, unsigned int tam_memoria_kb, TipoTabela tipo_tabela) {
    MMU *mmu = (MMU *)calloc(1, sizeof(MMU));
    if (!mmu) return NULL;

    strncpy(mmu->algoritmo, algoritmo, sizeof(mmu->algoritmo) - 1);
    mmu->tam_pagina_kb = tam_pagina_kb;
    mmu->tam_memoria_kb = tam_memoria_kb;
    mmu->num_quadros = tam_memoria_kb / tam_pagina_kb;
    mmu->quadros_ocupados = 0;
    mmu->ponteiro_clock = 0;

    unsigned int tam_pagina_bytes = tam_pagina_kb * 1024;
    unsigned int tmp = tam_pagina_bytes;
    mmu->shift_s = 0;
    while (tmp > 1) {
        tmp >>= 1;
        mmu->shift_s++;
    }

    unsigned int bits_vpn = 32 - mmu->shift_s;

    mmu->quadros = (Quadro *)calloc(mmu->num_quadros, sizeof(Quadro));
    mmu->tabela = tabela_criar(tipo_tabela, bits_vpn, mmu->num_quadros);

    srandom(42);

    return mmu;
}

void mmu_processar_acesso(MMU *mmu, unsigned int addr, char rw) {
    unsigned int vpn = addr >> mmu->shift_s;
    mmu->total_acessos++;

    int frame_id = tabela_buscar(mmu->tabela, vpn);

    if (frame_id != -1) {
        mmu->quadros[frame_id].ref = 1;
        mmu->quadros[frame_id].ultimo_acesso = mmu->total_acessos;
        if (rw == 'W' || rw == 'w') {
            mmu->quadros[frame_id].dirty = 1;
        }
        return;
    }

    mmu->paginas_lidas++;

    if (mmu->quadros_ocupados < mmu->num_quadros) {
        frame_id = mmu->quadros_ocupados++;
    } else {
        frame_id = selecionar_vitima(mmu);
        if (mmu->quadros[frame_id].dirty) {
            mmu->paginas_escritas++;
        }
        tabela_desmapear(mmu->tabela, mmu->quadros[frame_id].vpn);
    }

    mmu->quadros[frame_id].vpn = vpn;
    mmu->quadros[frame_id].ocupado = 1;
    mmu->quadros[frame_id].dirty = (rw == 'W' || rw == 'w') ? 1 : 0;
    mmu->quadros[frame_id].ref = 1;
    mmu->quadros[frame_id].ultimo_acesso = mmu->total_acessos;
    mmu->quadros[frame_id].tempo_carga = mmu->total_acessos;

    tabela_mapear(mmu->tabela, vpn, frame_id);
}

void mmu_destruir(MMU *mmu) {
    if (!mmu) return;
    if (mmu->tabela) {
        tabela_destruir(mmu->tabela);
    }
    if (mmu->quadros) {
        free(mmu->quadros);
    }
    free(mmu);
}
