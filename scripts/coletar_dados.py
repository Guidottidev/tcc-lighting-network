# -*- coding: utf-8 -*-
"""
coletar_dados.py - Etapa 1: baixa os dados brutos das fontes publicas.
Uso (na raiz do repositorio): python scripts/coletar_dados.py
Requer: Python 3.9+ e requests (pip install requests)

Salva cada arquivo EXATAMENTE como veio em data/raw/ e registra data da consulta,
URL, status HTTP e SHA-256 em data/raw/registro_coleta.csv. Nao altera, interpola
nem estima valores.

ATENCAO: os enderecos nao foram testados por quem escreveu o script. Se algum
falhar, o erro fica no CSV; confira a documentacao da fonte e ajuste a URL.
"""
import csv, hashlib, os
from datetime import date, datetime
import requests

RAW = os.path.join("data", "raw")
os.makedirs(RAW, exist_ok=True)
HOJE = date.today().isoformat()

FONTES = [
    ("mempool_lightning", f"mempool_lightning_all_{HOJE}.json",
     "https://mempool.space/api/v1/lightning/statistics/all",
     "mempool.space - estatisticas da Lightning (capacidade, nos, canais)"),
    ("defillama_lightning", f"defillama_lightning_{HOJE}.json",
     "https://api.llama.fi/protocol/lightning",
     "DeFiLlama - TVL da Lightning (slug 'lightning')"),
    ("defillama_lightning_alt", f"defillama_lightning_network_{HOJE}.json",
     "https://api.llama.fi/protocol/lightning-network",
     "DeFiLlama - TVL da Lightning (slug alternativo)"),
]

def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(8192), b""):
            h.update(bloco)
    return h.hexdigest()

linhas = []
for fid, arquivo, url, desc in FONTES:
    caminho = os.path.join(RAW, arquivo)
    status, erro, hash_ = "", "", ""
    try:
        r = requests.get(url, timeout=60, headers={"User-Agent": "tcc-coleta/1.0"})
        status = r.status_code
        if r.ok:
            with open(caminho, "wb") as f:
                f.write(r.content)
            hash_ = sha256(caminho)
        else:
            erro = f"HTTP {r.status_code}"
    except Exception as e:
        erro = str(e)[:200]
    linhas.append([fid, HOJE, datetime.now().isoformat(timespec="seconds"), url,
                   arquivo if hash_ else "", hash_, status, erro, desc])
    print("OK   " if hash_ else "FALHA", fid, erro)

destino = os.path.join(RAW, "registro_coleta.csv")
novo = not os.path.exists(destino)
with open(destino, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if novo:
        w.writerow(["id_fonte", "data_consulta", "momento_consulta", "url",
                    "arquivo_original", "sha256", "status_http", "erro", "descricao"])
    w.writerows(linhas)
