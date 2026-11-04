# tcc-lighting-network

Material suplementar (Apendices A e B) do Trabalho de Conclusao de Curso de Ciencias Economicas de Guilherme Guidotti de Souza (Fundacao Herminio Ometto - FHO), sobre indicadores publicos de infraestrutura da Lightning Network.

## Conteudo
- `data/raw/` - arquivos baixados exatamente como vieram das APIs, com `registro_coleta.csv` (data da consulta, URL, status HTTP e SHA-256 de cada arquivo).
- `data/base_tcc.csv` - base tratada, em formato longo (uma linha por indicador e data de referencia).
- `data/cobertura.csv` - quantas das 31 datas de referencia possuem registro em cada indicador.
- `scripts/` - codigo em Python: `coletar_dados.py`, `construir_base.py` e `figuras.py`.
- `figuras/` - figuras geradas a partir da base.
- `.github/workflows/coletar-dados.yml` - executa os tres scripts nos servidores do GitHub (acionamento manual em Actions).

## Fontes
- mempool.space - capacidade, canais e nos da Lightning Network (`/api/v1/lightning/statistics/all`).
- DeFiLlama - valor total bloqueado (TVL) (`/protocol/lightning-network`).

Dados consultados em 03/11/2026. Os valores devem ser conferidos nas fontes: as APIs podem ser revisadas e o endpoint `all` da mempool.space nao consta da lista de intervalos da documentacao consultada.

## Regras de tratamento
- 31 datas de referencia: ultimo dia de cada trimestre de 2018 a junho de 2025, mais 31/08/2025.
- Para cada data usa-se a observacao real mais proxima anterior ou igual a ela (tratamento T3); a data efetiva fica em `data_observacao`.
- Se a observacao anterior estiver a mais de 45 dias da data de referencia, a data fica sem registro. Nada e interpolado ou estimado.
- Conversoes de unidade (T1): satoshis para BTC; USD para milhoes de USD.

## Lacunas conhecidas
- Sem registro na mempool.space: 31/12/2021, 31/12/2023, 31/03/2024, 30/06/2024 e 30/09/2024.
- O TVL (DeFiLlama) possui registro em 19 das 31 datas, de 31/03/2021 a 31/08/2025.

## Limitacoes
- Os indicadores descrevem a infraestrutura observavel da rede. Nao medem volume de pagamentos, numero de usuarios ou comerciantes, nem custo de uma transferencia.
- A mempool.space informa os nos em quatro categorias (Tor, clearnet, nao anunciados e clearnet+Tor), sem total. Elas sao mantidas separadas e nao devem ser somadas sem confirmar a definicao na documentacao da fonte.
- Custo on-chain e TPS nao fazem parte desta versao, por falta de fonte verificada e por usarem metricas incomparaveis.
- Os maximos e minimos calculados a partir da base referem-se as datas de referencia, nao aos extremos da serie diaria.

## Como reproduzir
```
pip install requests pandas matplotlib
python scripts/coletar_dados.py
python scripts/construir_base.py
python scripts/figuras.py
```
Tambem e possivel executar pela aba Actions do GitHub (workflow "Coletar dados e gerar figuras"). Cada execucao baixa os dados novamente; os resultados podem diferir dos de 03/11/2026 se as fontes tiverem sido revisadas.
