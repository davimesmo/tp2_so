import csv
import os
import matplotlib.pyplot as plt
import numpy as np

def carregar_csv(caminho):
    dados = []
    with open(caminho, "r") as f:
        reader = csv.DictReader(f)
        for linha in reader:
            dados.append(linha)
    return dados

def plotar_cenario1():
    dados = carregar_csv("results/cenario1_memoria.csv")
    programas = sorted(list(set(d["programa"] for d in dados)))
    algoritmos = ["opt", "lru", "clock", "fifo", "random"]
    cores = {"opt": "#111111", "lru": "#1f77b4", "clock": "#2ca02c", "fifo": "#ff7f0e", "random": "#d62728"}
    estilos = {"opt": "--", "lru": "-", "clock": "-", "fifo": "-", "random": "-"}
    marcadores = {"opt": "^", "lru": "o", "clock": "s", "fifo": "D", "random": "x"}
    nomes = {"opt": "ÓTIMO (Teórico)", "lru": "LRU", "clock": "CLOCK", "fifo": "FIFO", "random": "RANDOM"}

    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    axs = axs.flatten()

    for idx, prog in enumerate(programas):
        ax = axs[idx]
        for alg in algoritmos:
            pontos = [d for d in dados if d["programa"] == prog and d["algoritmo"] == alg]
            pontos = sorted(pontos, key=lambda x: int(x["tam_memoria_kb"]))
            x = [int(p["tam_memoria_kb"]) for p in pontos]
            y = [int(p["paginas_lidas"]) for p in pontos]
            ax.plot(x, y, linestyle=estilos[alg], marker=marcadores[alg], label=nomes[alg], color=cores[alg], linewidth=1.8)

        ax.set_title(f"Programa: {prog}")
        ax.set_xlabel("Tamanho da Memória (KB)")
        ax.set_ylabel("Page Faults (Páginas Lidas)")
        ax.set_xscale("log", base=2)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(fontsize=8.5)

    plt.suptitle("Cenário 1: Page Faults com Memória Crescente (Páginas de 4 KB)", fontsize=14)
    plt.tight_layout()
    plt.savefig("results/cenario1_page_faults.png", dpi=300)
    plt.close()

def plotar_cenario2():
    dados = carregar_csv("results/cenario2_paginas.csv")
    programas = sorted(list(set(d["programa"] for d in dados)))
    algoritmos = ["opt", "lru", "clock", "fifo", "random"]
    cores = {"opt": "#111111", "lru": "#1f77b4", "clock": "#2ca02c", "fifo": "#ff7f0e", "random": "#d62728"}
    estilos = {"opt": "--", "lru": "-", "clock": "-", "fifo": "-", "random": "-"}
    marcadores = {"opt": "^", "lru": "o", "clock": "s", "fifo": "D", "random": "x"}
    nomes = {"opt": "ÓTIMO (Teórico)", "lru": "LRU", "clock": "CLOCK", "fifo": "FIFO", "random": "RANDOM"}

    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    axs = axs.flatten()

    for idx, prog in enumerate(programas):
        ax = axs[idx]
        for alg in algoritmos:
            pontos = [d for d in dados if d["programa"] == prog and d["algoritmo"] == alg]
            pontos = sorted(pontos, key=lambda x: int(x["tam_pagina_kb"]))
            x = [int(p["tam_pagina_kb"]) for p in pontos]
            y = [int(p["paginas_lidas"]) for p in pontos]
            ax.plot(x, y, linestyle=estilos[alg], marker=marcadores[alg], label=nomes[alg], color=cores[alg], linewidth=1.8)

        ax.set_title(f"Programa: {prog}")
        ax.set_xlabel("Tamanho da Página (KB)")
        ax.set_ylabel("Page Faults (Páginas Lidas)")
        ax.set_xscale("log", base=2)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(fontsize=8.5)

    plt.suptitle("Cenário 2: Page Faults com Tamanho de Página Variável (Memória 1024 KB)", fontsize=14)
    plt.tight_layout()
    plt.savefig("results/cenario2_page_faults.png", dpi=300)
    plt.close()

def plotar_cenario3_tabelas():
    dados3 = carregar_csv("results/cenario3_tabelas.csv")
    dados5 = carregar_csv("results/cenario5_alg_tabelas.csv")
    tabelas = ["densa", "hier2", "hier3", "invertida"]
    programas = ["compilador.log", "compressor.log", "matriz.log", "simulador.log"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    x = np.arange(len(tabelas))
    largura = 0.2
    cores_prog = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]

    for idx, prog in enumerate(programas):
        mems = []
        for tab in tabelas:
            p = [d for d in dados3 if d["programa"] == prog and d["tabela"] == tab][0]
            mems.append(int(p["memoria_tabela_bytes"]) / 1024.0)
        ax1.bar(x + (idx - 1.5) * largura, mems, largura, label=prog, color=cores_prog[idx])

    ax1.set_xticks(x)
    ax1.set_xticklabels(tabelas)
    ax1.set_title("Memória Alocada por Estrutura de Tabela (pag=4KB, mem=1024KB)")
    ax1.set_ylabel("Memória Alocada (KB) - Escala Log")
    ax1.set_yscale("log")
    ax1.grid(True, axis="y", linestyle="--", alpha=0.6)
    ax1.legend(fontsize=8.5)

    algs = ["lru", "clock", "fifo", "random"]
    cores_alg = {"lru": "#1f77b4", "clock": "#2ca02c", "fifo": "#ff7f0e", "random": "#d62728"}
    for idx, alg in enumerate(algs):
        tempos = []
        for tab in tabelas:
            p = [d for d in dados5 if d["algoritmo"] == alg and d["tabela"] == tab and int(d["tam_memoria_kb"]) == 1024][0]
            tempos.append(float(p["tempo_segundos"]))
        ax2.bar(x + (idx - 1.5) * largura, tempos, largura, label=alg.upper(), color=cores_alg[alg])

    ax2.set_xticks(x)
    ax2.set_xticklabels(tabelas)
    ax2.set_title("Tempo de Execução: Algoritmo x Tabela (compilador.log)")
    ax2.set_ylabel("Tempo (segundos)")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.6)
    ax2.legend(fontsize=8.5)

    plt.suptitle("Cenário 3: Custo de Memória e Tempo de Tradução das Tabelas de Páginas", fontsize=13)
    plt.tight_layout()
    plt.savefig("results/cenario3_tabelas.png", dpi=300)
    plt.close()

def plotar_cenario4_belady():
    dados = carregar_csv("results/cenario4_belady_escala.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    pontos_10k = [d for d in dados if int(d["tamanho_entrada"]) == 10000 and int(d["quadros"]) <= 18]
    q = [int(d["quadros"]) for d in pontos_10k]
    f_fifo = [int(d["faults_fifo"]) for d in pontos_10k]
    f_clock = [int(d["faults_clock"]) for d in pontos_10k]
    f_lru = [int(d["faults_lru"]) for d in pontos_10k]
    f_opt = [int(d["faults_opt"]) for d in pontos_10k]

    ax1.plot(q, f_fifo, marker="D", color="#ff7f0e", label="FIFO (Sofre Anomalia)", linewidth=2)
    ax1.plot(q, f_clock, marker="s", color="#2ca02c", label="CLOCK (Sofre Anomalia)", linestyle=":", linewidth=1.8)
    ax1.plot(q, f_lru, marker="o", color="#1f77b4", label="LRU (Algoritmo de Pilha - Imune)", linewidth=1.8)
    ax1.plot(q, f_opt, marker="^", color="#111111", linestyle="--", label="ÓTIMO (Algoritmo de Pilha - Imune)", linewidth=1.8)

    for i in range(1, len(q)):
        if f_fifo[i] > f_fifo[i - 1]:
            ax1.annotate("!", (q[i], f_fifo[i]), textcoords="offset points", xytext=(0, 6), ha="center", color="red", fontweight="bold")

    ax1.set_title("Curva em Dente-de-Serra da Anomalia de Belady (N=10.000)")
    ax1.set_xlabel("Número de Quadros Físicos")
    ax1.set_ylabel("Total de Page Faults")
    ax1.set_xticks(range(3, 19))
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(fontsize=8)

    tamanhos = [500, 2000, 10000, 50000]
    anomalias_fifo = []
    anomalias_clock = []
    anomalias_lru = []
    anomalias_opt = []

    for tam in tamanhos:
        pts = sorted([d for d in dados if int(d["tamanho_entrada"]) == tam], key=lambda x: int(x["quadros"]))
        c_fifo = sum(1 for i in range(1, len(pts)) if int(pts[i]["faults_fifo"]) > int(pts[i-1]["faults_fifo"]))
        c_clock = sum(1 for i in range(1, len(pts)) if int(pts[i]["faults_clock"]) > int(pts[i-1]["faults_clock"]))
        c_lru = sum(1 for i in range(1, len(pts)) if int(pts[i]["faults_lru"]) > int(pts[i-1]["faults_lru"]))
        c_opt = sum(1 for i in range(1, len(pts)) if int(pts[i]["faults_opt"]) > int(pts[i-1]["faults_opt"]))
        anomalias_fifo.append(c_fifo)
        anomalias_clock.append(c_clock)
        anomalias_lru.append(c_lru)
        anomalias_opt.append(c_opt)

    x = np.arange(len(tamanhos))
    w = 0.2
    ax2.bar(x - 1.5*w, anomalias_fifo, w, label="FIFO", color="#ff7f0e")
    ax2.bar(x - 0.5*w, anomalias_clock, w, label="CLOCK", color="#2ca02c")
    ax2.bar(x + 0.5*w, anomalias_lru, w, label="LRU (0 anomalias)", color="#1f77b4")
    ax2.bar(x + 1.5*w, anomalias_opt, w, label="ÓTIMO (0 anomalias)", color="#111111")

    ax2.set_xticks(x)
    ax2.set_xticklabels([f"N={t}" for t in tamanhos])
    ax2.set_title("Ocorrências da Anomalia de Belady (3 a 32 quadros)")
    ax2.set_xlabel("Tamanho da Sequência de Entrada (acessos)")
    ax2.set_ylabel("Qtd. de Transições Q -> Q+1 com Aumento de Faltas")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.6)
    ax2.legend(fontsize=8)

    plt.suptitle("Experimento Adicional 1: Escala da Anomalia de Belady vs. Algoritmos de Pilha", fontsize=13)
    plt.tight_layout()
    plt.savefig("results/cenario4_belady.png", dpi=300)
    plt.close()

def plotar_cenario5_dirty_bit():
    dados = carregar_csv("results/cenario1_memoria.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    mems = [128, 256, 512, 1024, 2048, 4096, 8192]
    algs = ["opt", "lru", "clock", "fifo"]
    cores = {"opt": "#111111", "lru": "#1f77b4", "clock": "#2ca02c", "fifo": "#ff7f0e"}

    pts_mat_lru = sorted([d for d in dados if d["programa"] == "matriz.log" and d["algoritmo"] == "lru" and int(d["tam_memoria_kb"]) in mems], key=lambda x: int(x["tam_memoria_kb"]))
    pts_mat_clk = sorted([d for d in dados if d["programa"] == "matriz.log" and d["algoritmo"] == "clock" and int(d["tam_memoria_kb"]) in mems], key=lambda x: int(x["tam_memoria_kb"]))

    x_m = [int(p["tam_memoria_kb"]) for p in pts_mat_lru]
    sem_dirty_lru = [max(0, int(p["paginas_lidas"]) - (int(p["tam_memoria_kb"]) // 4)) for p in pts_mat_lru]
    com_dirty_lru = [int(p["paginas_escritas"]) for p in pts_mat_lru]
    sem_dirty_clk = [max(0, int(p["paginas_lidas"]) - (int(p["tam_memoria_kb"]) // 4)) for p in pts_mat_clk]
    com_dirty_clk = [int(p["paginas_escritas"]) for p in pts_mat_clk]

    ax1.plot(x_m, sem_dirty_lru, linestyle="--", marker="o", color="#1f77b4", label="LRU Sem Dirty Bit (100% Dirty)")
    ax1.plot(x_m, com_dirty_lru, linestyle="-", marker="o", color="#1f77b4", label="LRU Com Dirty Bit (Real)")
    ax1.plot(x_m, sem_dirty_clk, linestyle="--", marker="s", color="#2ca02c", label="CLOCK Sem Dirty Bit (100% Dirty)")
    ax1.plot(x_m, com_dirty_clk, linestyle="-", marker="s", color="#2ca02c", label="CLOCK Com Dirty Bit (Real)")

    ax1.set_xscale("log", base=2)
    ax1.set_title("Escritas em Disco: Com vs. Sem Dirty Bit (matriz.log)")
    ax1.set_xlabel("Tamanho da Memória (KB)")
    ax1.set_ylabel("Páginas Escritas no Disco (Write-backs)")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(fontsize=8)

    progs = ["compilador.log", "compressor.log", "matriz.log", "simulador.log"]
    x_p = np.arange(len(progs))
    w = 0.2
    for idx, alg in enumerate(algs):
        taxas = []
        for prog in progs:
            p = [d for d in dados if d["programa"] == prog and d["algoritmo"] == alg and int(d["tam_memoria_kb"]) == 128][0]
            substituicoes = max(1, int(p["paginas_lidas"]) - 32)
            escritas = int(p["paginas_escritas"])
            economia = (1.0 - (escritas / substituicoes)) * 100.0
            taxas.append(economia)
        ax2.bar(x_p + (idx - 1.5) * w, taxas, w, label=alg.upper(), color=cores[alg])

    ax2.set_xticks(x_p)
    ax2.set_xticklabels([p.replace(".log", "") for p in progs])
    ax2.set_title("Economia de Escritas pelo Dirty Bit em 128 KB (%)")
    ax2.set_ylabel("Substituições Poupadas de Write-back (%)")
    ax2.set_ylim(0, 100)
    ax2.grid(True, axis="y", linestyle="--", alpha=0.6)
    ax2.legend(fontsize=8)

    plt.suptitle("Experimento Adicional 2: Impacto do Dirty Bit vs. Cenário 100% Dirty (LRU e CLOCK)", fontsize=13)
    plt.tight_layout()
    plt.savefig("results/cenario5_dirty_bit.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    print("Gerando graficos a partir dos resultados CSV...")
    plotar_cenario1()
    plotar_cenario2()
    plotar_cenario3_tabelas()
    plotar_cenario4_belady()
    plotar_cenario5_dirty_bit()
    print("Graficos salvos em results/.")
