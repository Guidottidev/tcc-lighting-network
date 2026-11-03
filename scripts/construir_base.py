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
"""
import json, os
import pandas as pd

DATAS = list(pd.date_range("2018-03-31", "2025-06-30", freq="QE")) + [pd.Timestamp("2025-08-31")]
RAW = os.path.join("data", "raw")
reg = pd.read_csv(os.path.join(RAW, "registro_coleta.csv"))
reg = reg[reg["arquivo_original"].notna() & (reg["arquivo_original"] != "")]

def ultimo(id_fonte):
    r = reg[reg["id_fonte"] == id_fonte]
    return None if r.empty else r.iloc[-1]

def carrega_mempool():
    r = ultimo("mempool_lightning")
    if r is None:
        return None, None
    dados = json.load(open(os.path.join(RAW, r["arquivo_original"]), encoding="utf-8"))
    if isinstance(dados, dict):
        for chave in ("data", "statistics", "items"):
            if chave in dados:
                dados = dados[chave]
                break
    df = pd.DataFrame(dados)
    df["obs"] = pd.to_datetime(df["added"], utc=True).dt.tz_localize(None).dt.normalize()
    return df.sort_values("obs"), r

def carrega_defillama():
    for fid in ("defillama_lightning", "defillama_lightning_alt"):
        r = ultimo(fid)
        if r is None:
            continue
        dados = json.load(open(os.path.join(RAW, r["arquivo_original"]), encoding="utf-8"))
        tvl = dados.get("tvl") or dados.get("chainTvls", {}).get("Bitcoin", {}).get("tvl")
        if tvl:
            df = pd.DataFrame(tvl)
            df["obs"] = pd.to_datetime(df["date"], unit="s").dt.normalize()
            return df.sort_values("obs"), r
    return None, None

def anterior(df, data):
    base = df[df["obs"] <= data]
    return None if base.empty else base.iloc[-1]

linhas = []
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

cols = ["data_referencia", "data_observacao", "data_consulta", "indicador", "valor",
        "unidade", "fonte", "url", "arquivo_original", "tratamentos"]
base = pd.DataFrame(linhas, columns=cols)
base.to_csv(os.path.join("data", "base_tcc.csv"), index=False)

cob = []
for ind in ["capacidade_btc", "nos", "canais", "tvl_usd_milhoes"]:
    b = base[base["indicador"] == ind]
    n_t3 = int(b["tratamentos"].str.contains("T3").sum()) if len(b) else 0
    cob.append([ind, len(DATAS), len(b), len(DATAS) - len(b), n_t3])
cob = pd.DataFrame(cob, columns=["indicador", "datas_esperadas", "registros", "faltando", "com_T3"])
cob.to_csv(os.path.join("data", "cobertura.csv"), index=False)
print(cob)
