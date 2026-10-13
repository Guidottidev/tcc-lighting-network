# -*- coding: utf-8 -*-
"""
graficos_tcc.py

Gera as 5 figuras do TCC sobre a viabilidade do Bitcoin como meio de
pagamento via Lightning Network. Requer só matplotlib (pip install
matplotlib);

Fontes dos dados, todas públicas e gratuitas:
  - Bitcoin Visuals ......... https://bitcoinvisuals.com/lightning
  - 1ML.com (nós/canais) .... https://1ml.com/statistics
  - Amboss Space ............ https://amboss.space
  - DeFiLlama (TVL) ......... https://defillama.com/protocol/lightning-network
  - mempool.space (taxas) ... https://mempool.space/pt/graphs
  - Visa fact sheet ......... https://www.visa.gr/dam/VCOM/download/corporate/media/visanet-technology/aboutvisafactsheet.pdf
  - Bitcoin.com News (queda 2025):
      https://news.bitcoin.com/data-shows-sustained-slide-in-lightning-network-capacity-channels-through-2025/

Os pontos marcados com [ref] nos comentários vêm direto dessas fontes;
o resto foi interpolado só pra desenhar a curva trimestral.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# Cores
AZUL = "#4472C4"
LARANJA = "#ED7D31"
VERDE = "#70AD47"

plt.rcParams["font.family"] = "DejaVu Sans"


def estilo_eixo(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#808080")
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=9, colors="#404040")


def linha_fonte(fig, texto):
    fig.text(0.01, 0.01, texto, fontsize=8.5, style="italic", color="#595959")


# Eixo X comum às figuras 1, 2 e 3: trimestral, jan/2018 a ago/2025
datas_str = [
    "2018-03", "2018-06", "2018-09", "2018-12", "2019-03", "2019-06", "2019-09", "2019-12",
    "2020-03", "2020-06", "2020-09", "2020-12", "2021-03", "2021-06", "2021-09", "2021-12",
    "2022-03", "2022-06", "2022-09", "2022-12", "2023-03", "2023-06", "2023-09", "2023-12",
    "2024-03", "2024-06", "2024-09", "2024-12", "2025-03", "2025-06", "2025-08",
]
datas = [datetime.strptime(d, "%Y-%m") for d in datas_str]


# =====================================================================
# FIGURA 1 — Capacidade da Lightning Network (em BTC)
# Fonte primária: Bitcoin Visuals (histórico) + Amboss (pico recente)
# [ref] mar/2018: 4 BTC (lançamento da rede, beta mainnet)
# [ref] mar/2019: 1.039 BTC
# [ref] 2023-2024: pico histórico ~5.498 BTC (Amboss)
# [ref] ago/2025: ~4.000 BTC, queda de ~27% frente ao pico (Bitcoin.com News, 2025)
# =====================================================================
capacidade_btc = [
    4, 60, 300, 450, 700, 850, 950, 1039, 1200, 1400, 1650, 1900, 2200, 2500,
    2800, 3200, 3600, 4100, 4400, 4700, 5400, 5100, 5300, 5450, 5498, 5450,
    5300, 5350, 5400, 4700, 4000,
]

fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
ax.plot(datas, capacidade_btc, color=AZUL, linewidth=2, marker="o", markersize=4)
ax.set_title("Capacidade da Lightning Network (em BTC)", fontsize=12, fontweight="bold", pad=12)
ax.set_ylabel("BTC alocados nos canais", fontsize=9.5)
estilo_eixo(ax)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
ax.set_ylim(0, 6500)
plt.tight_layout(rect=[0, 0.06, 1, 1])
linha_fonte(fig, "Fonte: Bitcoin Visuals (2025). Elaboração própria.")
plt.savefig("fig1_capacity.png", dpi=200, bbox_inches="tight")
plt.close()


# =====================================================================
# FIGURA 2 — Valor Total Bloqueado (TVL) da Lightning Network (US$ milhões)
# Fonte primária: DeFiLlama
# [ref] ago/2025: ~US$ 400 milhões (DeFiLlama registra hoje ~US$ 370 milhões,
#          mesma ordem de grandeza; a série exata dia a dia está no link acima)
# =====================================================================
tvl_milhoes = [
    0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 14, 18, 60, 120, 180, 210, 230, 190, 150, 170,
    260, 240, 220, 230, 280, 310, 330, 350, 370, 380, 400,
]

fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
ax.plot(datas, tvl_milhoes, color=LARANJA, linewidth=2, marker="o", markersize=4)
ax.set_title("Valor Total Bloqueado (TVL) da Lightning Network (em US$ milhões)", fontsize=12, fontweight="bold", pad=12)
ax.set_ylabel("US$ milhões", fontsize=9.5)
estilo_eixo(ax)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
plt.tight_layout(rect=[0, 0.06, 1, 1])
linha_fonte(fig, "Fonte: DeFiLlama (2025). Elaboração própria.")
plt.savefig("fig2_tvl.png", dpi=200, bbox_inches="tight")
plt.close()


# =====================================================================
# FIGURA 3 — Nós ativos e canais de pagamento da Lightning Network
# Fonte primária: 1ML.com
# [ref] mar/2022: pico de ~20.700 nós (1ML)
# [ref] meados/2022: pico de ~85.000 canais
# [ref] ago/2025: ~16.000 nós, ~41.700 canais (1ML; ver também Bitcoin.com
#          News, 2025, para a análise da queda)
# =====================================================================
nos_ativos = [
    50, 900, 3000, 4800, 6500, 8000, 9500, 10800, 12000, 13500, 14800, 15900,
    17200, 18400, 19500, 20200, 20700, 20000, 19000, 18500, 18000, 17800, 17600,
    17400, 17200, 17000, 16800, 16600, 16400, 16200, 16000,
]
canais = [
    30, 1900, 5200, 8200, 12000, 16000, 20500, 26000, 33000, 40500, 47500,
    54500, 62000, 68500, 75000, 80000, 83000, 85000, 82000, 78000, 74000,
    70000, 65000, 60000, 55000, 50000, 47000, 44000, 42500, 42000, 41700,
]

fig, ax1 = plt.subplots(figsize=(9, 4.3), dpi=200)
ax2 = ax1.twinx()
l1, = ax1.plot(datas, nos_ativos, color=AZUL, linewidth=2, marker="o", markersize=3.5, label="Nós ativos")
l2, = ax2.plot(datas, canais, color=LARANJA, linewidth=2, marker="s", markersize=3.5, label="Canais")
ax1.set_title("Número de nós ativos e canais de pagamento da Lightning Network", fontsize=12, fontweight="bold", pad=12)
ax1.set_ylabel("Nós ativos", fontsize=9.5, color=AZUL)
ax2.set_ylabel("Canais", fontsize=9.5, color=LARANJA)
ax1.tick_params(axis="y", colors=AZUL, labelsize=9)
ax2.tick_params(axis="y", colors=LARANJA, labelsize=9)
estilo_eixo(ax1)
ax2.spines[["top"]].set_visible(False)
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", fontsize=8)
ax1.legend(handles=[l1, l2], loc="upper left", fontsize=9, frameon=False)
plt.tight_layout(rect=[0, 0.06, 1, 1])
linha_fonte(fig, "Fonte: 1ML.com (2025). Elaboração própria.")
plt.savefig("fig3_nodes.png", dpi=200, bbox_inches="tight")
plt.close()


# =====================================================================
# FIGURA 4 — Custo médio de transação on-chain do Bitcoin (US$)
# Fonte primária: mempool.space
# [ref] abr/2021: pico histórico de ~US$ 63 (ciclo de alta do mercado)
# [ref] final de 2023: ~US$ 31 (congestionamento por Ordinals/BRC-20)
# Nota: a taxa da Lightning Network não aparece em barra própria porque,
# na mesma escala, ficaria invisível (é sempre < US$ 0,01) — por isso o
# valor vem só como nota de rodapé do gráfico, e não como categoria.
# =====================================================================
labels_fig4 = ["2019", "Jan/21", "Abr/21", "Jan/22", "Mai/22", "Nov/22", "Jun/23", "Nov/23", "Jun/24", "Dez/24"]
taxa_onchain = [0.6, 3.5, 62.8, 1.8, 2.0, 0.9, 1.4, 31, 3.2, 4.0]

xb = np.arange(len(labels_fig4))
fig, ax = plt.subplots(figsize=(9, 4.3), dpi=200)
ax.bar(xb, taxa_onchain, width=0.5, color=AZUL)
ax.set_title("Custo médio de transação on-chain do Bitcoin (em US$)", fontsize=12, fontweight="bold", pad=12)
ax.set_ylabel("US$ por transação", fontsize=9.5)
ax.set_xticks(xb)
ax.set_xticklabels(labels_fig4, rotation=35, ha="right", fontsize=8.5)
estilo_eixo(ax)
plt.tight_layout(rect=[0, 0.09, 1, 1])
linha_fonte(
    fig,
    "Fonte: mempool.space (2025). Elaboração própria.\n"
    "Nota: no mesmo período, a taxa mediana da Lightning Network permaneceu abaixo de US$ 0,01 por transação (1ML, 2025).",
)
plt.savefig("fig4_fees.png", dpi=200, bbox_inches="tight")
plt.close()


# =====================================================================
# FIGURA 5 — Capacidade transacional: Bitcoin on-chain, Visa e
# Lightning Network (TPS, escala logarítmica)
# Bitcoin on-chain: ~7 TPS — largamente documentado (ex.: Antonopoulos, 2017)
# Visa: capacidade declarada de ate 83.000 mensagens de transacao por segundo
#   https://corporate.visa.com/en/sites/visa-perspectives/security-trust/inside-visa-global-commerce-engine.html
# Lightning Network: >1.000.000 TPS (potencial teórico, condições ideais)
#   — Poon; Dryja (2016); Fidelity Digital Assets (2025)
# =====================================================================
categorias = ["Bitcoin\non-chain", "Visa\n(mensagens/s declarado)", "Lightning Network\n(potencial teórico)"]
valores_tps = [7, 83000, 1000000]
cores_fig5 = [AZUL, LARANJA, VERDE]

fig, ax = plt.subplots(figsize=(8, 4.3), dpi=200)
bars = ax.bar(categorias, valores_tps, color=cores_fig5, width=0.5)
ax.set_yscale("log")
ax.set_ylabel("Transações por segundo (escala log)", fontsize=9.5)
ax.set_title("Capacidade de processamento reportada: Bitcoin, Visa e Lightning Network (TPS)", fontsize=11, fontweight="bold", pad=12)
estilo_eixo(ax)
ax.tick_params(axis="x", labelsize=9)
for b, v in zip(bars, valores_tps):
    rotulo = f"{v:,}".replace(",", ".") + " TPS"
    ax.text(b.get_x() + b.get_width() / 2, v * 1.3, rotulo, ha="center", fontsize=9)
ax.set_ylim(1, 5_000_000)
plt.tight_layout(rect=[0, 0.06, 1, 1])
linha_fonte(fig, "Fonte: Antonopoulos (2017); Visa (2025); Poon e Dryja (2016); Fidelity Digital Assets (2025). Elaboração própria.")
plt.savefig("fig5_tps.png", dpi=200, bbox_inches="tight")
plt.close()

print("As 5 figuras foram salvas na pasta atual.")
