# -*- coding: utf-8 -*-
"""
construir_base.py - Etapa 2: monta a base tratada a partir de data/raw/.
Uso (na raiz do repositorio): python scripts/construir_base.py
Requer: pandas

Regras (as mesmas da planilha de controle):
- datas de referencia: ultimo dia de cada trimestre, 2018-2025, mais 2025-08-31;
- para cada data usa a observacao REAL mais proxima ANTERIOR (T3) e registra a data
  dessa observacao em data_observacao;
- se a observacao anterior estiver a mais de MAX_DEFASAGEM_DIAS da data de referencia,
  a data fica SEM registro (T6), para nao carregar um valor velho como se fosse atual;
- sem observacao anterior, a data tambem fica SEM registro (T6). Nada e interpolado;
- sats -> BTC e USD -> milhoes de USD (T1).

Correcao desta versao: o campo 'added' da mempool.space e um timestamp Unix em
SEGUNDOS (a versao anterior o lia como nanossegundos e gerava datas de 1970).

Nos: o arquivo da mempool.space traz quatro componentes (tor_nodes, clearnet_nodes,
unannounced_nodes, clearnet_tor_nodes) e nao um total. Eles sao registrados
separadamente; nao ha soma, porque a definicao de 'total de nos' deve ser confirmada
na documentacao da fonte antes de somar (clearnet_tor_nodes pode sobrepor outros).

Saidas: data/base_tcc.csv e data/cobertura.csv
"""
import json, os, traceback
import pandas as pd

MAX_DEFASAGEM_DIAS = 45
DATAS = list(pd.date_range("2018-03-31", "2025-06-30", freq="QE")) + [pd.Timestamp("2025-08-31")]
RAW = os.path.join("data", "raw")
REG = os.path.join(RAW, "registro_coleta.csv")
COLS_REG = ["id_fonte", "data_consulta", "momento_consulta", "url", "arquivo_original",
            "sha256", "status_http", "erro", "descricao"]

INDICADORES_MEMPOOL = [
    ("capacidade_btc", "total_capacity", "BTC", 1e-8),
    ("canais", "channel_count", "unidades", 1),
    ("nos_tor", "tor_nodes", "unidades", 1),
    ("nos_clearnet", "clearnet_nodes", "unidades", 1),
    ("nos_nao_anunciados", "unannounced_nodes", "unidades", 1),
    ("nos_clearnet_tor", "clearnet_tor_nodes", "unidades", 1),
]

print("Arquivos em data/raw:", sorted(os.listdir(RAW)) if os.path.isdir(RAW) else "PASTA NAO EXISTE")
reg = pd.read_csv(REG) if os.path.exists(REG) else pd.DataFrame(columns=COLS_REG)
if len(reg):
    print(reg[["id_fonte", "status_http", "erro"]].to_string())
reg = reg[reg["arquivo_original"].notna() & (reg["arquivo_original"].astype(str) != "")]

def ultimo(id_fonte):
    r = reg[reg["id_fonte"] == id_fonte]
    return None if r.empty else r.iloc[-1]

def carrega_mempool():
    r = ultimo("mempool_lightning")
    if r is None:
        print("mempool: sem arquivo baixado")
        return None, None
    dados = json.load(open(os.path.join(RAW, r["arquivo_original"]), encoding="utf-8"))
    if isinstance(dados, dict):
        for chave in ("data", "statistics", "items"):
            if chave in dados:
                dados = dados[chave]
                break
    df = pd.DataFrame(dados)
    print("mempool colunas:", list(df.columns))
    df["obs"] = pd.to_datetime(df["added"], unit="s").dt.normalize()
    df = df.sort_values("obs")
    print("mempool registros:", len(df), "| primeira obs:", df["obs"].min().date(),
          "| ultima obs:", df["obs"].max().date())
    return df, r

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
            df = df.sort_values("obs")
            print(fid, "registros:", len(df), "| primeira obs:", df["obs"].min().date(),
                  "| ultima obs:", df["obs"].max().date())
            return df, r
    print("defillama: sem serie de TVL utilizavel")
    return None, None

def carrega_blockchaininfo():
    r1 = ultimo("blockchaininfo_fees_usd")
    r2 = ultimo("blockchaininfo_n_tx")
    if r1 is None or r2 is None:
        print("blockchain.info: sem arquivos baixados")
        return None, None
    f1 = json.load(open(os.path.join(RAW, r1["arquivo_original"]), encoding="utf-8"))
    f2 = json.load(open(os.path.join(RAW, r2["arquivo_original"]), encoding="utf-8"))
    d1 = pd.DataFrame(f1["values"]).rename(columns={"x":"ts","y":"fees_usd"})
    d2 = pd.DataFrame(f2["values"]).rename(columns={"x":"ts","y":"n_tx"})
    df = pd.merge(d1, d2, on="ts", how="inner")
    df["obs"] = pd.to_datetime(df["ts"], unit="s").dt.normalize()
    df = df.sort_values("obs")
    df = df[df["n_tx"] > 0]
    df["custo_onchain_usd"] = df["fees_usd"] / df["n_tx"]
    print("blockchain.info registros:", len(df), "| primeira obs:", df["obs"].min().date(),
          "| ultima obs:", df["obs"].max().date())
    return df, r1

def anterior(df, data):
    base = df[df["obs"] <= data]
    if base.empty:
        return None
    o = base.iloc[-1]
    if (data - o["obs"]).days > MAX_DEFASAGEM_DIAS:
        return None
    return o

linhas = []
try:
    dfm, rm = carrega_mempool()
    if dfm is not None:
        for ind, col, un, conv in INDICADORES_MEMPOOL:
            if col not in dfm.columns:
                print(f"AVISO: campo '{col}' nao existe no arquivo; indicador '{ind}' ignorado")
                continue
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

try:
    dfb, rb = carrega_blockchaininfo()
    if dfb is not None:
        for d in DATAS:
            o = anterior(dfb, d)
            if o is None:
                continue
            trat = ["T5"] + (["T3"] if o["obs"] != d else [])
            linhas.append([d.date(), o["obs"].date(), rb["data_consulta"], "custo_onchain_usd",
                           float(o["custo_onchain_usd"]), "USD/tx", "Blockchain.com",
                           rb["url"], rb["arquivo_original"], ";".join(trat)])
except Exception:
    print("ERRO ao tratar Blockchain.com:")
    traceback.print_exc()

cols = ["data_referencia", "data_observacao", "data_consulta", "indicador", "valor",
        "unidade", "fonte", "url", "arquivo_original", "tratamentos"]
base = pd.DataFrame(linhas, columns=cols)
os.makedirs("data", exist_ok=True)
base.to_csv(os.path.join("data", "base_tcc.csv"), index=False)

cob = []
for ind in [i[0] for i in INDICADORES_MEMPOOL] + ["tvl_usd_milhoes", "custo_onchain_usd"]:
    b = base[base["indicador"] == ind]
    n_t3 = int(b["tratamentos"].str.contains("T3").sum()) if len(b) else 0
    cob.append([ind, len(DATAS), len(b), len(DATAS) - len(b), n_t3])
cob = pd.DataFrame(cob, columns=["indicador", "datas_esperadas", "registros", "faltando", "com_T3"])
cob.to_csv(os.path.join("data", "cobertura.csv"), index=False)
print(cob.to_string())
