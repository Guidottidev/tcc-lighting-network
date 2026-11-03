# tcc-lighting-network

Material suplementar (Apendices A e B) do TCC de Ciencias Economicas de Guilherme Guidotti de Souza (FHO), sobre indicadores publicos de infraestrutura da Lightning Network.

**Status: em construcao.** A base de dados ainda nao foi gerada. Os scripts abaixo coletam e tratam os dados, mas ainda nao foram executados com dados reais. Nenhum valor deste repositorio deve ser tratado como resultado ate que `data/base_tcc.csv` e `data/cobertura.csv` existam.

## Estrutura prevista
- `scripts/` - codigo em Python (coleta, construcao da base, figuras).
- `data/raw/` - arquivos baixados exatamente como vieram, com `registro_coleta.csv` (data da consulta, URL, SHA-256).
- `data/base_tcc.csv` - base tratada.
- `data/cobertura.csv` - quantas das 31 datas de referencia tem registro por indicador.
- `figuras/` - figuras geradas a partir da base.

## Como reproduzir
```
pip install requests pandas matplotlib
python scripts/coletar_dados.py
python scripts/construir_base.py
python scripts/figuras.py
```

## Regras
Nenhum valor e estimado ou interpolado. Para cada data de referencia (ultimo dia de cada trimestre de 2018 a 2025 e 31/08/2025) usa-se a observacao real mais proxima anterior, com a data efetiva em `data_observacao` e o codigo `T3` em `tratamentos`. Datas sem observacao anterior ficam sem registro. Conversoes de unidade: `T1`.

## Limitacoes
Os indicadores descrevem a infraestrutura observavel da rede. Nao medem volume de pagamentos, numero de usuarios ou comerciantes, nem custo total de uma transferencia. Custo on-chain e TPS nao fazem parte desta versao por falta de fonte verificada e por usarem metricas incomparaveis.
