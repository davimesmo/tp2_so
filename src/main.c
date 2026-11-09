#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "mmu.h"

static TipoTabela parse_tipo_tabela(const char *str) {
    if (!str) return TABELA_DENSA;
    if (strcasecmp(str, "hier2") == 0) return TABELA_HIER2;
    if (strcasecmp(str, "hier3") == 0) return TABELA_HIER3;
    if (strcasecmp(str, "invertida") == 0) return TABELA_INVERTIDA;
    return TABELA_DENSA;
}

int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr, "Uso: %s <algoritmo> <arquivo.log> <tam_pagina_KB> <tam_memoria_KB> [tipo_tabela]\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *algoritmo = argv[1];
    const char *nome_arquivo = argv[2];
    unsigned int tam_pagina_kb = (unsigned int)atoi(argv[3]);
    unsigned int tam_memoria_kb = (unsigned int)atoi(argv[4]);
    TipoTabela tipo_tabela = TABELA_DENSA;

    if (argc >= 6) {
        tipo_tabela = parse_tipo_tabela(argv[5]);
    }

    if (tam_pagina_kb == 0 || tam_memoria_kb == 0 || tam_memoria_kb < tam_pagina_kb) {
        fprintf(stderr, "Erro: parametros de tamanho invalidos.\n");
        return EXIT_FAILURE;
    }

    FILE *arquivo = fopen(nome_arquivo, "r");
    if (!arquivo) {
        fprintf(stderr, "Erro ao abrir arquivo: %s\n", nome_arquivo);
        return EXIT_FAILURE;
    }

    MMU *mmu = mmu_criar(algoritmo, tam_pagina_kb, tam_memoria_kb, tipo_tabela);
    if (!mmu) {
        fprintf(stderr, "Erro ao inicializar MMU.\n");
        fclose(arquivo);
        return EXIT_FAILURE;
    }

    unsigned int addr;
    char rw;

    while (fscanf(arquivo, "%x %c", &addr, &rw) == 2) {
        mmu_processar_acesso(mmu, addr, rw);
    }

    printf("Executando o simulador...\n");
    printf("Arquivo de entrada: %s\n", nome_arquivo);
    printf("Tamanho da memória: %u KB\n", tam_memoria_kb);
    printf("Tamanho das páginas: %u KB\n", tam_pagina_kb);
    printf("Técnica de reposição: %s\n", algoritmo);
    printf("Total de acessos à memória: %lu\n", mmu->total_acessos);
    printf("Páginas lidas: %lu\n", mmu->paginas_lidas);
    printf("Páginas escritas: %lu\n", mmu->paginas_escritas);

    if (argc >= 6) {
        printf("Memória da tabela: %zu bytes\n", tabela_memoria_usada(mmu->tabela));
    }

    fclose(arquivo);
    mmu_destruir(mmu);

    return EXIT_SUCCESS;
}
