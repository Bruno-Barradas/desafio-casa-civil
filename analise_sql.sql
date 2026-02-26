-- ============================================================
-- DESAFIO TÉCNICO - ANALISTA DE DADOS
-- Secretaria da Casa Civil - Escritório de Monitoramento
-- analise_sql.sql
-- ============================================================


-- ============================================================
-- PARTE 1: Localização de chamados do 1746 (Perguntas 1-5)
-- ============================================================

-- 1. Quantos chamados foram abertos no dia 01/04/2023?
SELECT
  COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE DATE(data_inicio) = '2023-04-01';


-- 2. Qual o tipo de chamado que teve mais chamados abertos no dia 01/04/2023?
SELECT
  tipo,
  COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE DATE(data_inicio) = '2023-04-01'
GROUP BY tipo
ORDER BY total_chamados DESC
LIMIT 1;


-- 3. Quais os nomes dos 3 bairros que mais tiveram chamados abertos nesse dia?
SELECT
  b.nome AS bairro,
  COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.dados_mestres.bairro` b
  ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
GROUP BY bairro
ORDER BY total_chamados DESC
LIMIT 3;


-- 4. Qual o nome da subprefeitura com mais chamados abertos nesse dia?
SELECT
  b.subprefeitura,
  COUNT(*) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.dados_mestres.bairro` b
  ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
GROUP BY b.subprefeitura
ORDER BY total_chamados DESC
LIMIT 1;


-- 5. Existe algum chamado aberto nesse dia que não foi associado a um bairro
--    ou subprefeitura na tabela de bairros? Se sim, por que isso acontece?
--
-- PASSO A: Contar chamados sem bairro associado
SELECT
  COUNT(*) AS total_chamados_sem_bairro
FROM `datario.adm_central_atendimento_1746.chamado` c
LEFT JOIN `datario.dados_mestres.bairro` b
  ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
  AND b.id_bairro IS NULL;

-- PASSO B: Listar os chamados sem bairro, mostrando seus detalhes
--   para entender o motivo (id_bairro será NULL ou não consta na tabela de bairros)
SELECT
  c.id_chamado,
  c.data_inicio,
  c.id_bairro,          -- NULL = chamado sem geolocalização
  c.tipo,
  c.subtipo,
  c.status,
  c.logradouro,
  c.numero_logradouro
FROM `datario.adm_central_atendimento_1746.chamado` c
LEFT JOIN `datario.dados_mestres.bairro` b
  ON c.id_bairro = b.id_bairro
WHERE DATE(c.data_inicio) = '2023-04-01'
  AND b.id_bairro IS NULL
ORDER BY c.data_inicio;

-- RESPOSTA / EXPLICAÇÃO:
-- Sim, existem chamados abertos nesse dia sem associação a bairro/subprefeitura.
-- Isso ocorre porque o campo id_bairro está NULL nessas ocorrências, o que indica
-- que o chamado foi registrado sem geolocalização válida. As causas mais comuns são:
--   • Chamados feitos por telefone sem endereço preciso ou incompleto
--   • Serviços/reclamações de caráter geral que não têm localização específica
--   • Erros de preenchimento ou cadastro no sistema 1746
-- Como o JOIN usa o campo id_bairro para cruzar com a tabela de bairros,
-- registros com id_bairro NULL nunca encontram correspondência e ficam sem
-- bairro ou subprefeitura associados.


-- ============================================================
-- PARTE 2: Chamados do 1746 em grandes eventos (Perguntas 6-10)
-- Subtipo: 5071 - Perturbação do sossego
-- Período: 01/01/2022 a 31/12/2024
-- ============================================================

-- 6. Quantos chamados de Perturbação do sossego foram abertos nesse período?
SELECT
  COUNT(*) AS total_chamados_perturbacao
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE id_subtipo = '5071'
  AND DATE(data_inicio) BETWEEN '2022-01-01' AND '2024-12-31';


-- 7. Selecione os chamados com esse subtipo que foram abertos
--    durante os eventos (Reveillon, Carnaval e Rock in Rio).
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
  AND DATE(c.data_inicio) BETWEEN '2022-01-01' AND '2024-12-31';


-- 8. Quantos chamados desse subtipo foram abertos em cada evento?
SELECT
  e.evento,
  e.data_inicial,
  e.data_final,
  COUNT(c.id_chamado) AS total_chamados
FROM `datario.adm_central_atendimento_1746.chamado` c
JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
  ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
WHERE c.id_subtipo = '5071'
  AND DATE(c.data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
GROUP BY e.evento, e.data_inicial, e.data_final
ORDER BY total_chamados DESC;


-- 9. Qual evento teve a maior média diária de chamados abertos desse subtipo?
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
LIMIT 1;


-- 10. Compare as médias diárias durante os eventos vs. todo o período.
WITH media_geral AS (
  SELECT
    COUNT(*) AS total_chamados,
    DATE_DIFF(DATE '2024-12-31', DATE '2022-01-01', DAY) + 1 AS total_dias,
    ROUND(
      COUNT(*) / (DATE_DIFF(DATE '2024-12-31', DATE '2022-01-01', DAY) + 1),
      2
    ) AS media_diaria_geral
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE id_subtipo = '5071'
    AND DATE(data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
),
media_eventos AS (
  SELECT
    e.evento,
    COUNT(c.id_chamado) AS total_chamados,
    DATE_DIFF(e.data_final, e.data_inicial, DAY) + 1 AS duracao_dias,
    ROUND(
      COUNT(c.id_chamado) / (DATE_DIFF(e.data_final, e.data_inicial, DAY) + 1),
      2
    ) AS media_diaria_evento
  FROM `datario.adm_central_atendimento_1746.chamado` c
  JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
    ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
  WHERE c.id_subtipo = '5071'
    AND DATE(c.data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
  GROUP BY e.evento, e.data_inicial, e.data_final
)
SELECT
  me.evento,
  me.media_diaria_evento,
  mg.media_diaria_geral,
  ROUND(me.media_diaria_evento - mg.media_diaria_geral, 2) AS diferenca,
  ROUND((me.media_diaria_evento / mg.media_diaria_geral - 1) * 100, 1) AS variacao_pct
FROM media_eventos me
CROSS JOIN media_geral mg
ORDER BY me.media_diaria_evento DESC;
