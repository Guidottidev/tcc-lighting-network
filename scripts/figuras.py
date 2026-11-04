# -*- coding: utf-8 -*-
"""
figuras.py - Etapa 3: gera as figuras a partir de data/base_tcc.csv.
Uso (na raiz do repositório): python scripts/figuras.py
Requer: pandas, matplotlib

- Lê SOMENTE a base. Não há números escritos no código.
- Plota apenas observações reais. Datas de referência sem registro (T6) ficam como
  lacuna: a linha é interrompida e NÃO é interpolada.
- As figuras NÃO trazem título nem fonte dentro da imagem: no texto do TCC, o título
  vai acima da figura e a fonte abaixo, conforme a norma (ABNT NBR 14724 / IBGE).
- Os quatro componentes de nós são mostrados separadamente, sem soma: a definição de
  'total de nós' deve ser confirmada na documentação da fonte (clearnet_tor_nodes
  pode sobrepor outros componentes).
- Figura 5: custo on-chain médio por transação = total de taxas diárias em dólares /
  número de transações confirmadas no dia (Blockchain.com). Não inclui o coinbase e
  não é o custo da Lightning. A linha tracejada é a média do trimestre (T7).
- Figura 6: transações confirmadas on-chain por dia (Blockchain.com). Nem toda
  transação é um pagamento por bens e serviços. Linha tracejada = média do trimestre.
Saídas: figuras/fig1_capacidade.png, fig2_tvl.png, fig3_canais.png,
fig4_nos.png, fig5_custo_onchain.png, fig6_transacoes_onchain.png
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATAS = list(pd.date_range("2018-03-31", "2026-09-30", freq="QE"))
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
    ax.set_xlim(pd.Timestamp("2018-01-01"), pd.Timestamp("2026-12-31"))

def salva(fig, arquivo):
    plt.tight_layout()
    plt.savefig(os.path.join("figuras", arquivo), bbox_inches="tight")
    plt.close(fig)

def uma(ind, rotulo, arquivo, media=None):
    s = serie(ind)
    if s.notna().sum() == 0:
        print("sem dados:", ind)
        return
    fig, ax = plt.subplots(figsize=(9, 4.0), dpi=200)
    ax.plot(s.index, s.values, marker="o", markersize=4, linewidth=1.5,
            label="Valor na data de referência")
    if media is not None:
        m = serie(media)
        if m.notna().sum():
            ax.plot(m.index, m.values, linestyle="--", linewidth=1.2, color="#B22222",
                    label="Média do trimestre")
        ax.legend(frameon=False, fontsize=8)
    ax.set_ylabel(rotulo)
    estilo(ax)
    salva(fig, arquivo)

uma("capacidade_btc", "BTC", "fig1_capacidade.png")
uma("tvl_usd_milhoes", "US$ milhões", "fig2_tvl.png")
uma("canais", "Número de canais", "fig3_canais.png")

componentes = [("nos_tor", "Tor"), ("nos_clearnet", "Clearnet"),
               ("nos_nao_anunciados", "Não anunciados"), ("nos_clearnet_tor", "Clearnet + Tor")]
fig, ax = plt.subplots(figsize=(9, 4.1), dpi=200)
algum = False
for ind, rotulo in componentes:
    s = serie(ind)
    if s.notna().sum():
        ax.plot(s.index, s.values, marker="o", markersize=3, linewidth=1.3, label=rotulo)
        algum = True
if algum:
    ax.set_ylabel("Número de nós")
    ax.legend(frameon=False, fontsize=8)
    estilo(ax)
    salva(fig, "fig4_nos.png")

uma("custo_onchain_usd", "US$ por transação", "fig5_custo_onchain.png",
    media="custo_onchain_usd_media_trim")
uma("transacoes_onchain_dia", "Transações por dia", "fig6_transacoes_onchain.png",
    media="transacoes_onchain_dia_media_trim")
print("figuras geradas em figuras/")
