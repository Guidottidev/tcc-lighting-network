# Base de dados e codigo - TCC Lightning Network

Material suplementar (Apendices A e B) do TCC de Ciencias Economicas de Guilherme Guidotti de Souza (FHO).

## Estrutura
- `data/raw/` - arquivos baixados exatamente como vieram, com `registro_coleta.csv` (data de consulta, URL, SHA-256).
- `data/base_tcc.csv` - base tratada (gerada por `construir_base.py`).
- `data/cobertura.csv` - quantas das 31 datas de referencia tem registro por indicador.
- `scripts/` - codigo em Python.
- `figuras/` - figuras geradas pela base.

## Como reproduzir
```
pip install requests pandas matplotlib
python scripts/coletar_dados.py
python scripts/construir_base.py
python scripts/figuras.py
```

## Regras
Nenhum valor e estimado ou interpolado. Para cada data de referencia (ultimo dia de cada trimestre de 2018 a 2025 e 31/08/2025) usa-se a observacao real mais proxima anterior, com a data efetiva em `data_observacao` e o codigo `T3` em `tratamentos`. Datas sem observacao anterior ficam sem registro. Conversoes: sats para BTC e USD para milhoes de USD (`T1`).

## Limitacoes
Os indicadores descrevem a infraestrutura observavel da rede. Nao medem volume de pagamentos, usuarios, comerciantes nem custo total de uma transferencia.
Custo on-chain e TPS nao fazem parte desta versao por falta de fonte verificada / metricas incomparaveis.
