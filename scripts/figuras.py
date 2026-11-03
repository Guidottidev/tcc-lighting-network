# -*- coding: utf-8 -*-
"""
figuras.py - Etapa 3: gera as figuras a partir de data/base_tcc.csv.
Uso (na raiz do repositorio): python scripts/figuras.py
Requer: pandas, matplotlib

- Le SOMENTE a base. Nao ha numeros escritos no codigo.
- Plota apenas observacoes reais; datas sem registro ficam sem ponto.
- Sem suavizacao e sem interpolacao.
- As figuras de TPS e de custo on-chain foram retiradas: a primeira compara metricas
  incompativeis; a segunda nao tem fonte verificada.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

os.makedirs("figuras", exist_ok=True)
b = pd.read_csv(os.path.join("data", "base_tcc.csv"), parse_dates=["data_referencia"])

def serie(ind):
    return b[b["indicador"] == ind].sort_values("data_referencia")

def estilo(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

def nota(fig, fonte):
    fig.text(0.01, 0.01, f"Fonte: {fonte}. Dados trimestrais (observacao real mais proxima anterior a data). Elaboracao propria.",
             fontsize=7.5, style="italic")

def uma(ind, titulo, rotulo, fonte, arquivo):
    s = serie(ind)
    if s.empty:
        print("sem dados:", ind)
        return
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
    ax.plot(s["data_referencia"], s["valor"], marker="o", markersize=4, linewidth=1.5)
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    ax.set_ylabel(rotulo)
    estilo(ax)
    nota(fig, fonte)
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(os.path.join("figuras", arquivo), bbox_inches="tight")
    plt.close()

uma("capacidade_btc", "Capacidade da Lightning Network", "BTC", "mempool.space", "fig1_capacidade.png")
uma("tvl_usd_milhoes", "Valor Total Bloqueado (TVL)", "US$ milhoes", "DeFiLlama", "fig2_tvl.png")

nos, can = serie("nos"), serie("canais")
if not nos.empty and not can.empty:
    fig, ax1 = plt.subplots(figsize=(9, 4.3), dpi=200)
    ax2 = ax1.twinx()
    ax1.plot(nos["data_referencia"], nos["valor"], marker="o", markersize=3.5, label="Nos")
    ax2.plot(can["data_referencia"], can["valor"], marker="s", markersize=3.5, color="#ED7D31", label="Canais")
    ax1.set_ylabel("Nos")
    ax2.set_ylabel("Canais")
    estilo(ax1)
    ax1.set_title("Nos e canais da Lightning Network", fontsize=12, fontweight="bold")
    nota(fig, "mempool.space")
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(os.path.join("figuras", "fig3_nos_canais.png"), bbox_inches="tight")
    plt.close()
