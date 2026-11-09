import csv
import os
import matplotlib.pyplot as plt

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
    algoritmos = ["lru", "clock", "fifo", "random"]
    cores = {"lru": "blue", "clock": "green", "fifo": "orange", "random": "red"}

    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    axs = axs.flatten()

    for idx, prog in enumerate(programas):
        ax = axs[idx]
        for alg in algoritmos:
            pontos = [d for d in dados if d["programa"] == prog and d["algoritmo"] == alg]
            pontos = sorted(pontos, key=lambda x: int(x["tam_memoria_kb"]))
            x = [int(p["tam_memoria_kb"]) for p in pontos]
            y = [int(p["paginas_lidas"]) for p in pontos]
            ax.plot(x, y, marker="o", label=alg.upper(), color=cores[alg])

        ax.set_title(f"Programa: {prog}")
        ax.set_xlabel("Tamanho da Memória (KB)")
        ax.set_ylabel("Page Faults (Páginas Lidas)")
        ax.set_xscale("log", base=2)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()

    plt.suptitle("Cenário 1: Page Faults com Memória Crescente (Páginas de 4 KB)", fontsize=14)
    plt.tight_layout()
    plt.savefig("results/cenario1_page_faults.png", dpi=300)
    plt.close()

def plotar_cenario2():
    dados = carregar_csv("results/cenario2_paginas.csv")
    programas = sorted(list(set(d["programa"] for d in dados)))
    algoritmos = ["lru", "clock", "fifo", "random"]
    cores = {"lru": "blue", "clock": "green", "fifo": "orange", "random": "red"}

    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    axs = axs.flatten()

    for idx, prog in enumerate(programas):
        ax = axs[idx]
        for alg in algoritmos:
            pontos = [d for d in dados if d["programa"] == prog and d["algoritmo"] == alg]
            pontos = sorted(pontos, key=lambda x: int(x["tam_pagina_kb"]))
            x = [int(p["tam_pagina_kb"]) for p in pontos]
            y = [int(p["paginas_lidas"]) for p in pontos]
            ax.plot(x, y, marker="s", label=alg.upper(), color=cores[alg])

        ax.set_title(f"Programa: {prog}")
        ax.set_xlabel("Tamanho da Página (KB)")
        ax.set_ylabel("Page Faults (Páginas Lidas)")
        ax.set_xscale("log", base=2)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()

    plt.suptitle("Cenário 2: Page Faults com Tamanho de Página Variável (Memória 1024 KB)", fontsize=14)
    plt.tight_layout()
    plt.savefig("results/cenario2_page_faults.png", dpi=300)
    plt.close()

def plotar_cenario3_tabelas():
    dados = carregar_csv("results/cenario3_tabelas.csv")
    tabelas = ["densa", "hier2", "hier3", "invertida"]
    
    prog_exemplo = "compilador.log"
    pontos = [d for d in dados if d["programa"] == prog_exemplo]

    mems = [int(p["memoria_tabela_bytes"]) / 1024 for tab in tabelas for p in pontos if p["tabela"] == tab]
    tempos = [float(p["tempo_segundos"]) for tab in tabelas for p in pontos if p["tabela"] == tab]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    ax1.bar(tabelas, mems, color=["#4285F4", "#34A853", "#FBBC05", "#EA4335"])
    ax1.set_title("Uso de Memória da Tabela (compilador.log)")
    ax1.set_ylabel("Memória Alocada (KB)")
    ax1.set_yscale("log")
    ax1.grid(True, axis="y", linestyle="--", alpha=0.6)

    ax2.bar(tabelas, tempos, color=["#4285F4", "#34A853", "#FBBC05", "#EA4335"])
    ax2.set_title("Tempo de Execução (compilador.log)")
    ax2.set_ylabel("Tempo (s)")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.6)

    plt.suptitle("Cenário 3: Comparação das Estruturas de Tabela de Páginas", fontsize=14)
    plt.tight_layout()
    plt.savefig("results/cenario3_tabelas.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    print("Gerando graficos a partir dos resultados CSV...")
    plotar_cenario1()
    plotar_cenario2()
    plotar_cenario3_tabelas()
    print("Graficos salvos em results/.")
