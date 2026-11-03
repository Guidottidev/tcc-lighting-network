# -*- coding: utf-8 -*-
"""
construir_base.py - Etapa 2: monta a base tratada a partir de data/raw/.
Uso (na raiz do repositorio): python scripts/construir_base.py
Requer: pandas

Regras (as mesmas da planilha de controle):
- datas de referencia: ultimo dia de cada trimestre, 2018-2025, mais 2025-08-31;
- para cada data usa a observacao REAL mais proxima ANTERIOR (T3) e registra a data
  dessa observacao em data_observacao;
- sem observacao anterior, a data fica SEM registro (T6). Nada e interpolado;
- sats -> BTC e USD -> milhoes de USD (T1).
Saidas: data/base_tcc.csv e data/cobertura.csv

Esta versao imprime diagnosticos no log (campos dos arquivos baixados) e nao
interrompe a execucao quando um indicador falha.
"""
import json, os, traceback
import pandas as pd

DATAS = list(pd.date_range("2018-03-31", "2025-06-30", freq="QE")) + [pd.Timestamp("2025-08-31")]
RAW = os.path.join("data", "raw")
REG = os.path.join(RAW, "registro_coleta.csv")
COLS_REG = ["id_fonte", "data_consulta", "momento_consulta", "url", "arquivo_original",
            "sha256", "status_http", "erro", "descricao"]

print("Arquivos em data/raw:", sorted(os.listdir(RAW)) if os.path.isdir(RAW) else "PASTA NAO EXISTE")
reg = pd.read_csv(REG) if os.path.exists(REG) else pd.DataFrame(columns=COLS_REG)
if len(reg):
    print(reg[["id_fonte", "status_http", "erro"]].to_string())
reg = reg[reg["arquivo_original"].notna() & (reg["arquivo_original"].astype(str) != "")]

def ultimo(id_fonte):
    r = reg[reg["id_fonte"] == id_fonte]
    return None if r.empty else r.iloc[-1]

def descreve(nome, dados):
    print(f"[{nome}] tipo:", type(dados).__name__)
    if isinstance(dados, dict):
        print(f"[{nome}] chaves:", list(dados.keys())[:30])
    elif isinstance(dados, list) and dados:
        print(f"[{nome}] n itens:", len(dados))
        print(f"[{nome}] primeiro item:", dados[0])
        print(f"[{nome}] ultimo item:", dados[-1])

def carrega_mempool():
    r = ultimo("mempool_lightning")
    if r is None:
        print("mempool: sem arquivo baixado")
        return None, None
    dados = json.load(open(os.path.join(RAW, r["arquivo_original"]), encoding="utf-8"))
    descreve("mempool", dados)
    if isinstance(dados, dict):
        for chave in ("data", "statistics", "items"):
            if chave in dados:
                dados = dados[chave]
                break
    df = pd.DataFrame(dados)
    print("mempool colunas:", list(df.columns))
    df["obs"] = pd.to_datetime(df["added"], utc=True).dt.tz_localize(None).dt.normalize()
    return df.sort_values("obs"), r

def carrega_defillama():
    for fid in ("defillama_lightning", "defillama_lightning_alt"):
        r = ultimo(fid)
        if r is None:
            continue
        dados = json.load(open(os.path.join(RAW, r["arquivo_original"]), encoding="utf-8"))
        descreve(fid, dados)
        tvl = dados.get("tvl") or dados.get("chainTvls", {}).get("Bitcoin", {}).get("tvl")
        if tvl:
            df = pd.DataFrame(tvl)
            print(fid, "colunas:", list(df.columns))
            df["obs"] = pd.to_datetime(df["date"], unit="s").dt.normalize()
            return df.sort_values("obs"), r
    print("defillama: sem serie de TVL utilizavel")
    return None, None

def anterior(df, data):
    base = df[df["obs"] <= data]
    return None if base.empty else base.iloc[-1]

linhas = []
try:
    dfm, rm = carrega_mempool()
    if dfm is not None:
        for ind, col, un, conv in [("capacidade_btc", "total_capacity", "BTC", 1e-8),
                                   ("nos", "node_count", "unidades", 1),
                                   ("canais", "channel_count", "unidades", 1)]:
            for d in DATAS:
                o = anterior(dfm, d)
                if o is None:
                    continue
                trat = (["T3"] if o["obs"] != d else []) + (["T1"] if ind == "capacidade_btc" else [])
                linhas.append([d.date(), o["obs"].date(), rm["data_consulta"], ind,
                               float(o[col]) * conv, un, "mempool.space",
                               rm["url"], rm["arquivo_original"], ";".join(trat)])
except Exception:
    print("ERRO ao tratar mempool.space:")
    traceback.print_exc()

try:
    dfd, rd = carrega_defillama()
    if dfd is not None:
        for d in DATAS:
            o = anterior(dfd, d)
            if o is None:
                continue
            trat = ["T1"] + (["T3"] if o["obs"] != d else [])
            linhas.append([d.date(), o["obs"].date(), rd["data_consulta"], "tvl_usd_milhoes",
                           float(o["totalLiquidityUSD"]) / 1e6, "milhoes USD", "DeFiLlama",
                           rd["url"], rd["arquivo_original"], ";".join(trat)])
except Exception:
    print("ERRO ao tratar DeFiLlama:")
    traceback.print_exc()

cols = ["data_referencia", "data_observacao", "data_consulta", "indicador", "valor",
        "unidade", "fonte", "url", "arquivo_original", "tratamentos"]
base = pd.DataFrame(linhas, columns=cols)
os.makedirs("data", exist_ok=True)
base.to_csv(os.path.join("data", "base_tcc.csv"), index=False)

cob = []
for ind in ["capacidade_btc", "nos", "canais", "tvl_usd_milhoes"]:
    b = base[base["indicador"] == ind]
    n_t3 = int(b["tratamentos"].str.contains("T3").sum()) if len(b) else 0
    cob.append([ind, len(DATAS), len(b), len(DATAS) - len(b), n_t3])
cob = pd.DataFrame(cob, columns=["indicador", "datas_esperadas", "registros", "faltando", "com_T3"])
cob.to_csv(os.path.join("data", "cobertura.csv"), index=False)
print(cob.to_string())
