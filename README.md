# tcc-lightning-network

Material suplementar (Apendices A e B) do Trabalho de Conclusao de Curso de Ciencias Economicas de Guilherme Guidotti de Souza (Fundacao Herminio Ometto - FHO), sobre a viabilidade do Bitcoin como meio de pagamento (uso e custo on-chain e infraestrutura da Lightning Network).

## Conteudo
- `data/raw/` - arquivos baixados exatamente como vieram das APIs, com `registro_coleta.csv` (data da consulta, URL, status HTTP e SHA-256 de cada arquivo).
- `data/base_tcc.csv` - base tratada, em formato longo (uma linha por indicador e data de referencia).
- `data/cobertura.csv` - quantas das 35 datas de referencia possuem registro em cada indicador.
- `scripts/` - codigo em Python: `coletar_dados.py`, `construir_base.py` e `figuras.py`.
- `figuras/` - figuras geradas a partir da base: `fig1_capacidade.png`, `fig2_tvl.png`, `fig3_canais.png`, `fig4_nos.png` e `fig5_custo_onchain.png, fig6_transacoes_onchain.png`.
- `.github/workflows/coletar-dados.yml` - executa os tres scripts nos servidores do GitHub (acionamento manual em Actions).

## Fontes
- mempool.space - capacidade, canais e nos da Lightning Network (`/api/v1/lightning/statistics/all`).
- DeFiLlama - valor total bloqueado (TVL) (`/protocol/lightning-network`).
- Blockchain.com - total diario de taxas em USD (`/charts/transaction-fees-usd`) e numero diario de transacoes confirmadas (`/charts/n-transactions`), usados para calcular o custo medio on-chain por transacao (taxas / transacoes; exclui o subsidio de bloco).

Dados consultados em 03 e 04/11/2026 (a base final usa os arquivos de 04/11/2026); as series brutas vao ate outubro/novembro de 2026 e a base usa as datas de referencia ate 30/09/2026. Os valores devem ser conferidos nas fontes: as APIs podem ser revisadas e o endpoint `all` da mempool.space nao consta da lista de intervalos da documentacao consultada.

## Regras de tratamento
- 35 datas de referencia: ultimo dia de cada trimestre de 31/03/2018 a 30/09/2026 (ultimo trimestre completo anterior a coleta).
- Para cada data usa-se a observacao real mais proxima anterior ou igual a ela (tratamento T3); a data efetiva fica em `data_observacao`.
- Se a observacao anterior estiver a mais de 45 dias da data de referencia, a data fica sem registro. Nada e interpolado ou estimado.
- Conversoes de unidade (T1): satoshis para BTC; USD para milhoes de USD.
- Razao calculada (T5): custo medio on-chain = taxas totais do dia em USD / transacoes confirmadas no dia.
- Sem registro (T6): data de referencia sem observacao a menos de 45 dias.
- Media trimestral (T7): para cada indicador, media das observacoes diarias do trimestre que termina na data de referencia (sufixo `_media_trim`; exige ao menos 60 observacoes no trimestre). Para o custo on-chain, a media e ponderada: soma das taxas do trimestre / soma das transacoes do trimestre.
- Descarte por inconsistencia da fonte (T8): a mempool.space nao publicou observacoes entre 10/03 e 25/08/2026 e, no retorno, registrou valores identicos em dias consecutivos (26 a 29/08/2026) seguidos de um snapshot de 3 canais e 0,22 BTC repetido por 52 dias (30/08 a 20/10/2026). Esses 56 registros sao descartados como falha de coleta da fonte; as datas 30/06/2026 e 30/09/2026 ficam sem registro para os indicadores da mempool.space. A observacao de 21/10/2026 (22.680 canais; 2.531 BTC) e posterior ao periodo e nao e utilizada.

## Lacunas conhecidas
- Sem registro na mempool.space: 31/12/2021, 31/12/2023, 31/03/2024, 30/06/2024, 30/09/2024, 30/06/2026 e 30/09/2026 (7 de 35 datas).
- O TVL (DeFiLlama) possui registro em 23 das 35 datas, de 31/03/2021 a 30/09/2026.
- O custo on-chain e as transacoes on-chain (Blockchain.com) possuem registro nas 35 datas.
- A serie diaria da mempool.space apresenta, em alguns dias, contagens de canais e nos sensivelmente menores que as dos dias vizinhos (provavel sincronizacao parcial do grafo da rede). Esses dias nao sao removidos; as medias trimestrais (T7) atenuam o efeito.

## Limitacoes
- Os indicadores descrevem a infraestrutura observavel da rede. Nao medem volume de pagamentos, numero de usuarios ou comerciantes, nem custo de uma transferencia.
- A mempool.space informa os nos em quatro categorias (Tor, clearnet, nao anunciados e clearnet+Tor), sem total. Elas sao mantidas separadas e nao devem ser somadas sem confirmar a definicao na documentacao da fonte.
- O valor principal de cada indicador refere-se a um unico dia (a data de referencia); a media trimestral (T7) e registrada separadamente como medida de robustez. Nao existe nesta base nenhuma medida do custo de um pagamento na Lightning Network, nem de TPS.
- Os maximos e minimos calculados a partir da base referem-se as datas de referencia, nao aos extremos da serie diaria.

## Como reproduzir
```
pip install requests pandas matplotlib
python scripts/coletar_dados.py
python scripts/construir_base.py
python scripts/figuras.py
```
Tambem e possivel executar pela aba Actions do GitHub (workflow "Coletar dados e gerar figuras"). Cada execucao baixa os dados novamente; os resultados podem diferir dos de 04/11/2026 se as fontes tiverem sido revisadas.


## Indicadores adicionais

- `transacoes_onchain_dia`: numero de transacoes confirmadas on-chain por dia (Blockchain.com, serie `n-transactions`), valor bruto da fonte na data de referencia. Indicador de uso direto do Bitcoin; nem toda transacao e um pagamento por bens e servicos (inclui, por exemplo, inscricoes de dados a partir de 2023). Figura 6.
