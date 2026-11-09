import os
import subprocess
import time
import csv

PROGRAMAS = [
    "compilador.log",
    "compressor.log",
    "matriz.log",
    "simulador.log"
]

ALGORITMOS = ["lru", "clock", "fifo", "random"]
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

if __name__ == "__main__":
    print("Iniciando bateria de experimentos...")
    rodar_cenario1()
    rodar_cenario2()
    rodar_cenario3_tabelas()
    print("Experimentos concluidos com sucesso.")
