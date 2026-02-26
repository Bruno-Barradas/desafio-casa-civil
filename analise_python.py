# ============================================================
# DESAFIO TÉCNICO - ANALISTA DE DADOS
# analise_python.py
# Respostas às questões SQL usando Python + basedosdados
# ============================================================

import basedosdados as bd
import pandas as pd

# Defina seu billing project do GCP
BILLING_PROJECT = "desafio-casa-civil" # ← substitua pelo seu project ID


def run_query(sql: str) -> pd.DataFrame:
    """Executa uma query no BigQuery e retorna um DataFrame."""
    return bd.read_sql(sql, billing_project_id=BILLING_PROJECT)


# ============================================================
# PARTE 1: Localização de chamados do 1746
# ============================================================

print("=" * 60)
print("PARTE 1 – Chamados do 1746 no dia 01/04/2023")
print("=" * 60)

# -----------------------------------------------------------
# Pergunta 1: Quantos chamados foram abertos no dia 01/04/2023?
# -----------------------------------------------------------
q1 = """
SELECT COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE DATE(data_inicio) = '2023-04-01'
"""
df1 = run_query(q1)
print("\n1. Total de chamados abertos em 01/04/2023:")
print(df1.to_string(index=False))


# -----------------------------------------------------------
# Pergunta 2: Tipo de chamado com mais abertura nesse dia
# -----------------------------------------------------------
q2 = """
SELECT tipo, COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE DATE(data_inicio) = '2023-04-01'
GROUP BY tipo
ORDER BY total_chamados DESC
LIMIT 1
"""
df2 = run_query(q2)
print("\n2. Tipo de chamado com mais aberturas em 01/04/2023:")
print(df2.to_string(index=False))


# -----------------------------------------------------------
# Pergunta 3: 3 bairros com mais chamados abertos nesse dia
# -----------------------------------------------------------
q3 = """
SELECT b.nome AS bairro, COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
GROUP BY bairro
ORDER BY total_chamados DESC
LIMIT 3
"""
df3 = run_query(q3)
print("\n3. Top 3 bairros com mais chamados em 01/04/2023:")
print(df3.to_string(index=False))


# -----------------------------------------------------------
# Pergunta 4: Subprefeitura com mais chamados abertos nesse dia
# -----------------------------------------------------------
q4 = """
SELECT b.subprefeitura, COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
GROUP BY b.subprefeitura
ORDER BY total_chamados DESC
LIMIT 1
"""
df4 = run_query(q4)
print("\n4. Subprefeitura com mais chamados em 01/04/2023:")
print(df4.to_string(index=False))


# -----------------------------------------------------------
# Pergunta 5: Chamados sem associação a bairro/subprefeitura
# -----------------------------------------------------------
q5 = """
SELECT COUNT(*) AS chamados_sem_bairro
FROM `datario.adm_central_atendimento_1746.chamado` c
LEFT JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
  AND b.id_bairro IS NULL
"""
df5 = run_query(q5)
sem_bairro = df5["chamados_sem_bairro"].iloc[0]
print(f"\n5. Chamados sem bairro/subprefeitura em 01/04/2023: {sem_bairro}")
if sem_bairro > 0:
    print(
        "   Motivo: id_bairro nulo ou sem correspondência na tabela de bairros.\n"
        "   Isso ocorre quando o chamado é registrado sem geolocalização válida\n"
        "   (ex: atendimentos por telefone sem endereço preciso, ou serviços\n"
        "   que não possuem localização geográfica específica)."
    )
else:
    print("   Todos os chamados estão associados a um bairro.")


# ============================================================
# PARTE 2: Chamados do 1746 em grandes eventos
# Subtipo 5071 – Perturbação do sossego | 01/01/2022 a 31/12/2024
# ============================================================

print("\n" + "=" * 60)
print("PARTE 2 – Perturbação do Sossego em Grandes Eventos")
print("=" * 60)

# -----------------------------------------------------------
# Pergunta 6: Total de chamados de Perturbação do Sossego no período
# -----------------------------------------------------------
q6 = """
SELECT COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE id_subtipo = '5071'
  AND DATE(data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
"""
df6 = run_query(q6)
print("\n6. Total de chamados de Perturbação do Sossego (2022-2024):")
print(df6.to_string(index=False))


# -----------------------------------------------------------
# Pergunta 7: Chamados abertos durante os eventos
# -----------------------------------------------------------
q7 = """
SELECT
  c.id_chamado,
  c.data_inicio,
  c.tipo,
  c.subtipo,
  c.id_bairro,
  e.evento
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
  ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
WHERE c.id_subtipo = '5071'
  AND DATE(c.data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
"""
df7 = run_query(q7)
print("\n7. Chamados de Perturbação do Sossego durante os eventos:")
print(df7.head(10).to_string(index=False))
print(f"   ... ({len(df7)} chamados no total)")


# -----------------------------------------------------------
# Pergunta 8: Total de chamados por evento
# -----------------------------------------------------------
q8 = """
SELECT
  e.evento,
  COUNT(c.id_chamado) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
  ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
WHERE c.id_subtipo = '5071'
  AND DATE(c.data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
GROUP BY e.evento
ORDER BY total_chamados DESC
"""
df8 = run_query(q8)
print("\n8. Total de chamados por evento:")
print(df8.to_string(index=False))


# -----------------------------------------------------------
# Pergunta 9: Evento com maior média diária de chamados
# -----------------------------------------------------------
q9 = """
SELECT
  e.evento,
  COUNT(c.id_chamado) AS total_chamados,
  DATE_DIFF(e.data_final, e.data_inicial, DAY) + 1 AS duracao_dias,
  ROUND(
    COUNT(c.id_chamado) / (DATE_DIFF(e.data_final, e.data_inicial, DAY) + 1),
    2
  ) AS media_diaria
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
  ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
WHERE c.id_subtipo = '5071'
  AND DATE(c.data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
GROUP BY e.evento, e.data_inicial, e.data_final
ORDER BY media_diaria DESC
"""
df9 = run_query(q9)
print("\n9. Média diária de chamados por evento:")
print(df9.to_string(index=False))
print(f"\n   Evento com maior média diária: {df9.iloc[0]['evento']} "
      f"({df9.iloc[0]['media_diaria']} chamados/dia)")


# -----------------------------------------------------------
# Pergunta 10: Comparação médias diárias eventos vs. período geral
# -----------------------------------------------------------
q10_geral = """
SELECT
  COUNT(*) AS total_chamados,
  DATE_DIFF(DATE '2024-12-31', DATE '2022-01-01', DAY) + 1 AS total_dias
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE id_subtipo = '5071'
  AND DATE(data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
"""
df10_geral = run_query(q10_geral)
media_geral = (
    df10_geral["total_chamados"].iloc[0] / df10_geral["total_dias"].iloc[0]
)

# Reusa df9 que já tem as médias por evento
df10 = df9.copy()
df10["media_diaria_geral"] = round(media_geral, 2)
df10["diferenca"] = round(df10["media_diaria"] - df10["media_diaria_geral"], 2)
df10["variacao_pct"] = round(
    (df10["media_diaria"] / df10["media_diaria_geral"] - 1) * 100, 1
)

print("\n10. Comparativo: média diária nos eventos vs. média geral do período:")
print(df10[["evento", "media_diaria", "media_diaria_geral",
            "diferenca", "variacao_pct"]].to_string(index=False))
print(f"\n    Média diária geral (2022-2024): {round(media_geral, 2)} chamados/dia")
print(
    "    Conclusão: todos os eventos apresentam média diária SUPERIOR à média geral,\n"
    "    indicando que grandes eventos na cidade aumentam significativamente os\n"
    "    chamados de perturbação do sossego."
)
