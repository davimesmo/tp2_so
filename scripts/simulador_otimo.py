import os
import sys
import time
import csv
import subprocess

PROGRAMAS = [
    "compilador.log",
    "compressor.log",
    "matriz.log",
    "simulador.log"
]

TAM_MEMORIA_C1 = [128, 256, 512, 1024, 2048, 4096, 8192, 16384]
TAM_PAGINA_C2 = [2, 4, 8, 16, 32, 64]
TABELAS = ["densa", "hier2", "hier3", "invertida"]

CACHE_TRACES = {}


def carregar_trace(caminho_arquivo):
    """Lê o arquivo de log uma vez e retorna listas de endereços (int) e operações ('R'/'W')."""
    if caminho_arquivo in CACHE_TRACES:
        return CACHE_TRACES[caminho_arquivo]

    addrs = []
    rws = []
    with open(caminho_arquivo, "r") as f:
        for linha in f:
            partes = linha.split()
            if len(partes) >= 2:
                addrs.append(int(partes[0], 16))
                rws.append(partes[1].upper())
    CACHE_TRACES[caminho_arquivo] = (addrs, rws)
    return addrs, rws


def simular_otimo_dados(addrs, rws, tam_pagina_kb, tam_memoria_kb):
    """
    Executa o Algoritmo Ótimo de Belady (MIN) sobre os vetores de endereços e operações,
    produzindo exatamente os mesmos resultados (páginas lidas e páginas escritas) que a MMU em C.
    """
    num_quadros = tam_memoria_kb // tam_pagina_kb
    tam_pagina_bytes = tam_pagina_kb * 1024

    shift_s = 0
    tmp = tam_pagina_bytes
    while tmp > 1:
        tmp >>= 1
        shift_s += 1

    n = len(addrs)
    vpns = [addr >> shift_s for addr in addrs]

    # Pré-processamento reverso O(N): calcula o índice da próxima aparição futura de cada acesso
    INF = n + 1
    proximos_acessos = [INF] * n
    ultima_aparicao = {}

    for i in range(n - 1, -1, -1):
        vpn = vpns[i]
        proximos_acessos[i] = ultima_aparicao.get(vpn, INF)
        ultima_aparicao[vpn] = i

    # Estruturas da MMU (idênticas ao simulador em C)
    quadros_vpn = [0] * num_quadros
    quadros_dirty = [0] * num_quadros
    quadros_prox = [0] * num_quadros
    tabela_vpn_para_quadro = {}

    quadros_ocupados = 0
    paginas_lidas = 0
    paginas_escritas = 0

    for i in range(n):
        vpn = vpns[i]
        rw = rws[i]
        prox = proximos_acessos[i]

        frame_id = tabela_vpn_para_quadro.get(vpn, -1)

        if frame_id != -1:
            # Page Hit
            quadros_prox[frame_id] = prox
            if rw == "W":
                quadros_dirty[frame_id] = 1
            continue

        # Page Fault
        paginas_lidas += 1

        if quadros_ocupados < num_quadros:
            frame_id = quadros_ocupados
            quadros_ocupados += 1
        else:
            # Escolhe o quadro cujo próximo acesso está mais distante no futuro
            vitima = 0
            mais_distante = quadros_prox[0]
            for q in range(1, num_quadros):
                if quadros_prox[q] > mais_distante:
                    mais_distante = quadros_prox[q]
                    vitima = q

            frame_id = vitima
            if quadros_dirty[frame_id]:
                paginas_escritas += 1

            del tabela_vpn_para_quadro[quadros_vpn[frame_id]]

        quadros_vpn[frame_id] = vpn
        quadros_dirty[frame_id] = 1 if rw == "W" else 0
        quadros_prox[frame_id] = prox
        tabela_vpn_para_quadro[vpn] = frame_id

    return {
        "total_acessos": n,
        "paginas_lidas": paginas_lidas,
        "paginas_escritas": paginas_escritas,
    }


def simular_otimo_arquivo(caminho_arquivo, tam_pagina_kb, tam_memoria_kb):
    t0 = time.time()
    addrs, rws = carregar_trace(caminho_arquivo)
    res = simular_otimo_dados(addrs, rws, tam_pagina_kb, tam_memoria_kb)
    res["tempo_segundos"] = round(time.time() - t0, 4)
    return res


def executar_simulador_c(algoritmo, arquivo, tam_pagina, tam_memoria, tabela=None):
    cmd = ["./simulador", algoritmo, arquivo, str(tam_pagina), str(tam_memoria)]
    if tabela:
        cmd.append(tabela)

    t_inicio = time.time()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    t_fim = time.time()

    paginas_lidas = 0
    paginas_escritas = 0
    memoria_tabela = 0

    for linha in res.stdout.splitlines():
        if "Páginas lidas:" in linha:
            paginas_lidas = int(linha.split(":")[1].strip())
        elif "Páginas escritas:" in linha:
            paginas_escritas = int(linha.split(":")[1].strip())
        elif "Memória da tabela:" in linha:
            memoria_tabela = int(linha.split(":")[1].replace("bytes", "").strip())

    return {
        "paginas_lidas": paginas_lidas,
        "paginas_escritas": paginas_escritas,
        "memoria_tabela_bytes": memoria_tabela,
        "tempo_segundos": round(t_fim - t_inicio, 4),
    }


def atualizar_cenario1_com_otimo():
    os.makedirs("results", exist_ok=True)
    caminho_csv = "results/cenario1_memoria.csv"
    linhas_existentes = []
    if os.path.exists(caminho_csv):
        with open(caminho_csv, "r") as f:
            linhas_existentes = [r for r in csv.DictReader(f) if r["algoritmo"] != "opt"]

    novas_opt = []
    for prog in PROGRAMAS:
        caminho_prog = os.path.join("tp2-files", prog)
        for mem in TAM_MEMORIA_C1:
            print(f"[Ótimo - Cenário 1] {prog} | opt | mem={mem}KB pag=4KB")
            r = simular_otimo_arquivo(caminho_prog, 4, mem)
            novas_opt.append({
                "programa": prog,
                "algoritmo": "opt",
                "tam_pagina_kb": 4,
                "tam_memoria_kb": mem,
                "paginas_lidas": r["paginas_lidas"],
                "paginas_escritas": r["paginas_escritas"],
                "tempo_segundos": r["tempo_segundos"]
            })

    todas = novas_opt + linhas_existentes
    with open(caminho_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "programa", "algoritmo", "tam_pagina_kb", "tam_memoria_kb",
            "paginas_lidas", "paginas_escritas", "tempo_segundos"
        ])
        writer.writeheader()
        writer.writerows(todas)


def atualizar_cenario2_com_otimo():
    os.makedirs("results", exist_ok=True)
    caminho_csv = "results/cenario2_paginas.csv"
    mem_fixa = 1024
    linhas_existentes = []
    if os.path.exists(caminho_csv):
        with open(caminho_csv, "r") as f:
            linhas_existentes = [r for r in csv.DictReader(f) if r["algoritmo"] != "opt"]

    novas_opt = []
    for prog in PROGRAMAS:
        caminho_prog = os.path.join("tp2-files", prog)
        for pag in TAM_PAGINA_C2:
            print(f"[Ótimo - Cenário 2] {prog} | opt | mem={mem_fixa}KB pag={pag}KB")
            r = simular_otimo_arquivo(caminho_prog, pag, mem_fixa)
            novas_opt.append({
                "programa": prog,
                "algoritmo": "opt",
                "tam_pagina_kb": pag,
                "tam_memoria_kb": mem_fixa,
                "paginas_lidas": r["paginas_lidas"],
                "paginas_escritas": r["paginas_escritas"],
                "tempo_segundos": r["tempo_segundos"]
            })

    todas = novas_opt + linhas_existentes
    with open(caminho_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "programa", "algoritmo", "tam_pagina_kb", "tam_memoria_kb",
            "paginas_lidas", "paginas_escritas", "tempo_segundos"
        ])
        writer.writeheader()
        writer.writerows(todas)


def rodar_experimento_belady_escala():
    os.makedirs("results", exist_ok=True)
    os.makedirs("tests", exist_ok=True)

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
                r_fifo = executar_simulador_c("fifo", arq_teste, 4, mem_kb)
                r_clock = executar_simulador_c("clock", arq_teste, 4, mem_kb)
                r_lru = executar_simulador_c("lru", arq_teste, 4, mem_kb)
                r_opt = simular_otimo_arquivo(arq_teste, 4, mem_kb)
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
            print(f"[Belady Escala + Ótimo] Concluído para N={tam} acessos (3 a 32 quadros)")


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
                    r = executar_simulador_c(alg, os.path.join("tp2-files", "compilador.log"), 4, mem, tab)
                    writer.writerow({
                        "programa": "compilador.log",
                        "algoritmo": alg,
                        "tabela": tab,
                        "tam_memoria_kb": mem,
                        "memoria_tabela_bytes": r["memoria_tabela_bytes"],
                        "tempo_segundos": r["tempo_segundos"]
                    })
                    f.flush()
    print("[Cenário 5] Matriz Algoritmo x Tabela concluída.")


def main():
    
    if len(sys.argv) >= 4:
        caminho_arquivo = sys.argv[1]
        tam_pagina_kb = int(sys.argv[2])
        tam_memoria_kb = int(sys.argv[3])

        res = simular_otimo_arquivo(caminho_arquivo, tam_pagina_kb, tam_memoria_kb)

        print("Executando o simulador (Módulo Ótimo Teórico)...")
        print(f"Arquivo de entrada: {caminho_arquivo}")
        print(f"Tamanho da memória: {tam_memoria_kb} KB")
        print(f"Tamanho das páginas: {tam_pagina_kb} KB")
        print("Técnica de reposição: opt")
        print(f"Total de acessos à memória: {res['total_acessos']}")
        print(f"Páginas lidas: {res['paginas_lidas']}")
        print(f"Páginas escritas: {res['paginas_escritas']}")
        return

    print("Iniciando bateria de testes do Algoritmo Ótimo e experimentos extras...")
    atualizar_cenario1_com_otimo()
    atualizar_cenario2_com_otimo()
    rodar_experimento_belady_escala()
    rodar_cenario5_alg_vs_tabelas()
    print("Todos os CSVs com métricas do Ótimo foram atualizados em results/.")


if __name__ == "__main__":
    main()
