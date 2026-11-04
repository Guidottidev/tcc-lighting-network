# -*- coding: utf-8 -*-
"""
figuras.py - Etapa 3: gera as figuras a partir de data/base_tcc.csv.
Uso (na raiz do repositorio): python scripts/figuras.py
Requer: pandas, matplotlib

- Le SOMENTE a base. Nao ha numeros escritos no codigo.
- Plota apenas observacoes reais. Datas de referencia sem registro (T6) ficam como
  lacuna: a linha e interrompida e NAO e interpolada.
- Os quatro componentes de nos sao mostrados separadamente, sem soma: a definicao de
  'total de nos' deve ser confirmada na documentacao da fonte (clearnet_tor_nodes
  pode sobrepor outros componentes).
- A figura de TPS foi retirada (compara metricas incompativeis).
- A Figura 5 agora mostra o custo on-chain medio por transacao, calculado como
  total de taxas diarias em dolares dividido pelo numero de transacoes confirmadas
  no mesmo dia (Blockchain.com). Nao inclui o coinbase, e nao e o custo da Lightning.
Saidas: figuras/fig1_capacidade.png, fig2_tvl.png, fig3_canais.png,
fig4_nos.png, fig5_custo_onchain.png, fig6_transacoes_onchain.png
- A Figura 6 mostra o numero de transacoes confirmadas on-chain por dia (Blockchain.com),
  indicador de uso direto do Bitcoin. Nem toda transacao e um pagamento por bens e servicos.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATAS = list(pd.date_range("2018-03-31", "2025-06-30", freq="QE")) + [pd.Timestamp("2025-08-31")]
os.makedirs("figuras", exist_ok=True)
b = pd.read_csv(os.path.join("data", "base_tcc.csv"), parse_dates=["data_referencia"])

def serie(ind):
    s = b[b["indicador"] == ind].set_index("data_referencia")["valor"]
    return s.reindex(DATAS)

def estilo(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

def nota(fig, fonte):
    fig.text(0.01, 0.01,
             f"Fonte: {fonte}. Datas de referencia trimestrais; lacunas indicam datas sem observacao disponivel. Elaboracao propria.",
             fontsize=7, style="italic")

def salva(fig, arquivo):
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(os.path.join("figuras", arquivo), bbox_inches="tight")
    plt.close(fig)

def uma(ind, titulo, rotulo, fonte, arquivo):
    s = serie(ind)
    if s.notna().sum() == 0:
        print("sem dados:", ind)
        return
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
    ax.plot(s.index, s.values, marker="o", markersize=4, linewidth=1.5)
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    ax.set_ylabel(rotulo)
    estilo(ax)
    nota(fig, fonte)
    salva(fig, arquivo)

uma("capacidade_btc", "Capacidade da Lightning Network", "BTC", "mempool.space", "fig1_capacidade.png")
uma("tvl_usd_milhoes", "Valor Total Bloqueado (TVL)", "US$ milhoes", "DeFiLlama", "fig2_tvl.png")
uma("canais", "Canais da Lightning Network", "Numero de canais", "mempool.space", "fig3_canais.png")

componentes = [("nos_tor", "Tor"), ("nos_clearnet", "Clearnet"),
               ("nos_nao_anunciados", "Nao anunciados"), ("nos_clearnet_tor", "Clearnet + Tor")]
fig, ax = plt.subplots(figsize=(9, 4.3), dpi=200)
algum = False
for ind, rotulo in componentes:
    s = serie(ind)
    if s.notna().sum():
        ax.plot(s.index, s.values, marker="o", markersize=3, linewidth=1.3, label=rotulo)
        algum = True
if algum:
    ax.set_title("Nos da Lightning Network por tipo de conectividade", fontsize=12, fontweight="bold")
    ax.set_ylabel("Numero de nos")
    ax.legend(frameon=False, fontsize=8)
    estilo(ax)
    nota(fig, "mempool.space")
    salva(fig, "fig4_nos.png")

uma("custo_onchain_usd",
    "Custo medio on-chain do Bitcoin por transacao",
    "US$ por transacao",
    "Blockchain.com (taxas totais / numero de transacoes)",
    "fig5_custo_onchain.png")


uma("transacoes_onchain_dia",
    "Transacoes on-chain do Bitcoin confirmadas por dia",
    "Transacoes por dia",
    "Blockchain.com (n-transactions)",
    "fig6_transacoes_onchain.png")
