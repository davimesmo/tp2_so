import os
import subprocess
import time
import csv
import random

PROGRAMAS = [
    "compilador.log",
    "compressor.log",
    "matriz.log",
    "simulador.log"
]

ALGORITMOS = ["opt", "lru", "clock", "fifo", "random"]
TAM_MEMORIA_C1 = [128, 256, 512, 1024, 2048, 4096, 8192, 16384]
TAM_PAGINA_C2 = [2, 4, 8, 16, 32, 64]
TABELAS = ["densa", "hier2", "hier3", "invertida"]

def executar_simulador(algoritmo, arquivo, tam_pagina, tam_memoria, tabela=None):
    cmd = ["./simulador", algoritmo, arquivo, str(tam_pagina), str(tam_memoria)]
    if tabela:
        cmd.append(tabela)

    t_inicio = time.time()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    t_fim = time.time()

    total_acessos = 0
    paginas_lidas = 0
    paginas_escritas = 0
    memoria_tabela = 0

    for linha in res.stdout.splitlines():
        if "Total de acessos à memória:" in linha:
            total_acessos = int(linha.split(":")[1].strip())
        elif "Páginas lidas:" in linha:
            paginas_lidas = int(linha.split(":")[1].strip())
        elif "Páginas escritas:" in linha:
            paginas_escritas = int(linha.split(":")[1].strip())
        elif "Memória da tabela:" in linha:
            memoria_tabela = int(linha.split(":")[1].replace("bytes", "").strip())

    return {
        "programa": os.path.basename(arquivo),
        "algoritmo": algoritmo,
        "tam_pagina_kb": tam_pagina,
        "tam_memoria_kb": tam_memoria,
        "tabela": tabela if tabela else "densa",
        "total_acessos": total_acessos,
        "paginas_lidas": paginas_lidas,
        "paginas_escritas": paginas_escritas,
        "memoria_tabela_bytes": memoria_tabela,
        "tempo_segundos": round(t_fim - t_inicio, 4)
    }

def rodar_cenario1():
    os.makedirs("results", exist_ok=True)
    caminho_csv = "results/cenario1_memoria.csv"
    with open(caminho_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "programa", "algoritmo", "tam_pagina_kb", "tam_memoria_kb",
            "paginas_lidas", "paginas_escritas", "tempo_segundos"
        ])
        writer.writeheader()

        for prog in PROGRAMAS:
            caminho_prog = os.path.join("tp2-files", prog)
            for alg in ALGORITMOS:
                for mem in TAM_MEMORIA_C1:
                    print(f"[Cenario 1] {prog} | {alg} | mem={mem}KB pag=4KB")
                    r = executar_simulador(alg, caminho_prog, 4, mem)
                    writer.writerow({
                        "programa": r["programa"],
                        "algoritmo": r["algoritmo"],
                        "tam_pagina_kb": r["tam_pagina_kb"],
                        "tam_memoria_kb": r["tam_memoria_kb"],
                        "paginas_lidas": r["paginas_lidas"],
                        "paginas_escritas": r["paginas_escritas"],
                        "tempo_segundos": r["tempo_segundos"]
                    })
                    f.flush()

def rodar_cenario2():
    os.makedirs("results", exist_ok=True)
    caminho_csv = "results/cenario2_paginas.csv"
    mem_fixa = 1024
    with open(caminho_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "programa", "algoritmo", "tam_pagina_kb", "tam_memoria_kb",
            "paginas_lidas", "paginas_escritas", "tempo_segundos"
        ])
        writer.writeheader()

        for prog in PROGRAMAS:
            caminho_prog = os.path.join("tp2-files", prog)
            for alg in ALGORITMOS:
                for pag in TAM_PAGINA_C2:
                    print(f"[Cenario 2] {prog} | {alg} | mem={mem_fixa}KB pag={pag}KB")
                    r = executar_simulador(alg, caminho_prog, pag, mem_fixa)
                    writer.writerow({
                        "programa": r["programa"],
                        "algoritmo": r["algoritmo"],
                        "tam_pagina_kb": r["tam_pagina_kb"],
                        "tam_memoria_kb": r["tam_memoria_kb"],
                        "paginas_lidas": r["paginas_lidas"],
                        "paginas_escritas": r["paginas_escritas"],
                        "tempo_segundos": r["tempo_segundos"]
                    })
                    f.flush()

def rodar_cenario3_tabelas():
    os.makedirs("results", exist_ok=True)
    caminho_csv = "results/cenario3_tabelas.csv"
    with open(caminho_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "programa", "tabela", "tam_pagina_kb", "tam_memoria_kb",
            "memoria_tabela_bytes", "tempo_segundos"
        ])
        writer.writeheader()

        for prog in PROGRAMAS:
            caminho_prog = os.path.join("tp2-files", prog)
            for tab in TABELAS:
                print(f"[Cenario 3] {prog} | tabela={tab}")
                r = executar_simulador("lru", caminho_prog, 4, 1024, tab)
                writer.writerow({
                    "programa": r["programa"],
                    "tabela": r["tabela"],
                    "tam_pagina_kb": r["tam_pagina_kb"],
                    "tam_memoria_kb": r["tam_memoria_kb"],
                    "memoria_tabela_bytes": r["memoria_tabela_bytes"],
                    "tempo_segundos": r["tempo_segundos"]
                })
                f.flush()

def rodar_experimento_belady_escala():
    os.makedirs("results", exist_ok=True)
    os.makedirs("tests", exist_ok=True)
    random.seed(42)

    padrao_belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    tamanhos_entrada = [500, 2000, 10000, 50000]
    caminho_csv = "results/cenario4_belady_escala.csv"

    with open(caminho_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "tamanho_entrada", "quadros", "mem_kb",
            "faults_fifo", "faults_clock", "faults_lru", "faults_opt"
        ])
        writer.writeheader()

        for tam in tamanhos_entrada:
            arq_teste = f"tests/trace_belady_{tam}.log"
            with open(arq_teste, "w") as tf:
                fase = 0
                gerados = 0
                while gerados < tam:
                    k = [5, 7, 9, 11, 13, 15][fase % 6]
                    base = (fase % 3) * 32
                    seq = list(range(1, k)) + list(range(1, k - 2)) + [k] + list(range(1, k + 1))
                    # Repete o mesmo padrao 20 vezes seguidas para estabilizar naquela janela
                    for _ in range(20):
                        for p in seq:
                            if gerados >= tam:
                                break
                            vpn = base + p
                            rw = "W" if (gerados % 3 == 0) else "R"
                            tf.write(f"{vpn * 0x1000:08x} {rw}\n")
                            gerados += 1
                        if gerados >= tam:
                            break
                    fase += 1

            for q in range(3, 33):
                mem_kb = q * 4
                r_fifo = executar_simulador("fifo", arq_teste, 4, mem_kb)
                r_clock = executar_simulador("clock", arq_teste, 4, mem_kb)
                r_lru = executar_simulador("lru", arq_teste, 4, mem_kb)
                r_opt = executar_simulador("opt", arq_teste, 4, mem_kb)
                writer.writerow({
                    "tamanho_entrada": tam,
                    "quadros": q,
                    "mem_kb": mem_kb,
                    "faults_fifo": r_fifo["paginas_lidas"],
                    "faults_clock": r_clock["paginas_lidas"],
                    "faults_lru": r_lru["paginas_lidas"],
                    "faults_opt": r_opt["paginas_lidas"]
                })
                f.flush()
            print(f"[Belady Escala] Concluido para N={tam} acessos (3 a 32 quadros)")

    caminho_real_belady = "results/cenario4_belady_reais.csv"
    with open(caminho_real_belady, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "programa", "quadros", "mem_kb", "faults_fifo", "faults_clock", "faults_lru", "faults_opt"
        ])
        writer.writeheader()
        for prog in ["compilador.log", "matriz.log", "simulador.log"]:
            caminho_prog = os.path.join("tp2-files", prog)
            for q in range(16, 81, 2):
                mem_kb = q * 4
                r_fifo = executar_simulador("fifo", caminho_prog, 4, mem_kb)
                r_clock = executar_simulador("clock", caminho_prog, 4, mem_kb)
                r_lru = executar_simulador("lru", caminho_prog, 4, mem_kb)
                r_opt = executar_simulador("opt", caminho_prog, 4, mem_kb)
                writer.writerow({
                    "programa": prog,
                    "quadros": q,
                    "mem_kb": mem_kb,
                    "faults_fifo": r_fifo["paginas_lidas"],
                    "faults_clock": r_clock["paginas_lidas"],
                    "faults_lru": r_lru["paginas_lidas"],
                    "faults_opt": r_opt["paginas_lidas"]
                })
                f.flush()
            print(f"[Belady Traces Reais] Concluido varredura fina para {prog}")

def rodar_cenario5_alg_vs_tabelas():
    os.makedirs("results", exist_ok=True)
    caminho_csv = "results/cenario5_alg_tabelas.csv"
    with open(caminho_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "programa", "algoritmo", "tabela", "tam_memoria_kb", "memoria_tabela_bytes", "tempo_segundos"
        ])
        writer.writeheader()
        for alg in ["lru", "clock", "fifo", "random"]:
            for tab in TABELAS:
                for mem in [128, 1024, 8192]:
                    r = executar_simulador(alg, os.path.join("tp2-files", "compilador.log"), 4, mem, tab)
                    writer.writerow({
                        "programa": "compilador.log",
                        "algoritmo": alg,
                        "tabela": tab,
                        "tam_memoria_kb": mem,
                        "memoria_tabela_bytes": r["memoria_tabela_bytes"],
                        "tempo_segundos": r["tempo_segundos"]
                    })
                    f.flush()
    print("[Cenario 5] Matriz Algoritmo x Tabela concluida.")

if __name__ == "__main__":
    print("Iniciando bateria de experimentos...")
    rodar_cenario1()
    rodar_cenario2()
    rodar_cenario3_tabelas()
    rodar_experimento_belady_escala()
    rodar_cenario5_alg_vs_tabelas()
    print("Experimentos concluidos com sucesso.")
