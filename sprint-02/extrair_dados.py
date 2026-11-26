"""Gera as bases de entrada do notebook a partir dos arquivos públicos.

Fontes (repositório público do grupo: Joaopdiasventura/fleet-force-calculation-engine):
  - despesa-veiculos-ufmg-2025.pdf  (SISFROTA, Relatório de Despesas por Veículo, 01/01 a 31/12/2025)
  - Preços semestrais - AUTOMOTIVOS_2026.01.csv  (ANP, levantamento de preços, 1º semestre de 2026)

Uso:
  python extrair_dados.py --pdf dados/despesa-veiculos-ufmg-2025.pdf --anp "<caminho do CSV da ANP>"

Saídas:
  dados/frota_ufmg_2025_bruto.csv : uma linha por linha impressa no PDF, sem nenhuma limpeza
  dados/anp_mg_2026s1.csv         : só as coletas de Minas Gerais (o CSV nacional tem 72 MB)
"""
import argparse
import re
from pathlib import Path

import pandas as pd
import pdfplumber

AQUI = Path(__file__).resolve().parent

# Limites horizontais das colunas (em pontos), medidos no cabeçalho do PDF.
# A ordem visual das colunas é a do cabeçalho impresso.
LIMITES = [35, 90, 180, 210, 260, 310, 360, 410, 455, 495, 545, 605, 655, 725, 780]
COLUNAS = [
    "placa", "modelo", "qtd_os", "mao_obra_interna", "mao_obra_externa",
    "pecas", "pneus", "abastecimento", "lubrificante", "lavagem", "km",
    "km_l_relatorio", "despesa_total", "custo_km_relatorio",
]
PLACA = re.compile(r"[A-Z0-9]{7}")


def numero_us(texto: str):
    """O relatório usa vírgula de milhar e ponto decimal: 3,650.38."""
    texto = (texto or "").strip()
    return float(texto.replace(",", "")) if texto else None


def coluna_de(x: float):
    for i, (esq, dir_) in enumerate(zip(LIMITES[:-1], LIMITES[1:])):
        if esq <= x < dir_:
            return i
    return None


def extrair_frota(pdf_path: Path) -> pd.DataFrame:
    linhas = []
    with pdfplumber.open(pdf_path) as pdf:
        for n_pag, pag in enumerate(pdf.pages, start=1):
            palavras = pag.extract_words(x_tolerance=1, y_tolerance=1.2)
            ancoras = sorted({round(p["top"], 1) for p in palavras
                              if 40 <= p["x0"] < 90 and PLACA.fullmatch(p["text"])})
            for y in ancoras:
                baldes = [[] for _ in COLUNAS]
                for p in palavras:
                    if abs(p["top"] - y) <= 0.8:
                        i = coluna_de((p["x0"] + p["x1"]) / 2)
                        if i is not None:
                            baldes[i].append(p)
                valores = [" ".join(p["text"] for p in sorted(b, key=lambda q: q["x0"])) for b in baldes]
                reg = dict(zip(COLUNAS, valores))
                reg["pagina_pdf"] = n_pag
                linhas.append(reg)
    df = pd.DataFrame(linhas)
    for c in COLUNAS[2:]:
        df[c] = df[c].map(numero_us)
    return df


def extrair_anp_mg(csv_path: Path) -> pd.DataFrame:
    partes = []
    for bloco in pd.read_csv(csv_path, sep=";", encoding="latin-1", dtype=str, chunksize=200_000):
        bloco.columns = [c.replace("﻿", "").replace("ï»¿", "").strip() for c in bloco.columns]
        partes.append(bloco[bloco["Estado - Sigla"] == "MG"])
    mg = pd.concat(partes, ignore_index=True)
    mg = mg[["Municipio", "Produto", "Data da Coleta", "Valor de Venda", "Bandeira"]].copy()
    mg.columns = ["municipio", "produto", "data_coleta", "preco_venda", "bandeira"]
    mg["preco_venda"] = mg["preco_venda"].str.replace(",", ".").astype(float)
    mg["data_coleta"] = pd.to_datetime(mg["data_coleta"], format="%d/%m/%Y")
    return mg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--anp", type=Path, required=True)
    args = ap.parse_args()
    saida = AQUI / "dados"
    saida.mkdir(exist_ok=True)

    frota = extrair_frota(args.pdf)
    frota.to_csv(saida / "frota_ufmg_2025_bruto.csv", index=False, encoding="utf-8")
    print(f"frota: {len(frota)} linhas, {frota['placa'].nunique()} placas")

    anp = extrair_anp_mg(args.anp)
    anp.to_csv(saida / "anp_mg_2026s1.csv", index=False, encoding="utf-8")
    print(f"anp MG: {len(anp)} coletas, produtos: {sorted(anp['produto'].unique())}")


if __name__ == "__main__":
    main()
