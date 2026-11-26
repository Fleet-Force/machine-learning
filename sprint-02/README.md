# Fleet Force | Sprint 2 | Machine Learning & Modelling

Análise exploratória, limpeza e preparação de dados de uma frota real (UFMG, 2025) para o Challenge Sem Parar da FIAP (turma 1TIAPR, 2026), equipe Fleet Force.

O notebook principal é `fleet_force_ml_sprint2.ipynb`: já vem executado, com saídas e gráficos.

## Dados

| Arquivo | Origem |
|---|---|
| `dados/despesa-veiculos-ufmg-2025.pdf` | Relatório de Despesas por Veículo (SISFROTA) da UFMG, 01/01 a 31/12/2025 |
| `dados/frota_ufmg_2025_bruto.csv` | Tabela do PDF extraída por `extrair_dados.py`, sem limpeza |
| `dados/anp_mg_2026s1.csv` | Preços de combustível da ANP, só Minas Gerais, 1º semestre de 2026 (recorte do arquivo nacional de 72 MB) |
| `dados/frota_ufmg_2025_limpa.csv` | Saída do notebook: um veículo por linha, com categoria e marcações de qualidade |

## Como rodar

```
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute fleet_force_ml_sprint2.ipynb
```

Para regenerar os CSVs de entrada a partir dos arquivos originais:

```
python extrair_dados.py --pdf dados/despesa-veiculos-ufmg-2025.pdf --anp "Preços semestrais - AUTOMOTIVOS_2026.01.csv"
```
