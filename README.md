# Desafio Técnico – Analista de Dados
**Escritório de Monitoramento de Projetos e Metas – Secretaria da Casa Civil / Rio de Janeiro**

---

## Sobre o Projeto

Este repositório contém a solução completa para o Desafio Técnico de Analista de Dados da Prefeitura do Rio de Janeiro (2026). O desafio foi dividido em três partes: análise SQL via BigQuery, integração com APIs externas e visualização de dados.

🔗 **Dashboard interativo:** https://bruno-barradas-desafio-casa-civil.streamlit.app

---

## Resultados

### Parte 1 — Chamados do 1746 (01/04/2023)

- **2.067 chamados** abertos no dia
- Tipo mais frequente: **Estacionamento irregular (373)**
- Bairro líder: **Campo Grande (125)**
- Subprefeitura líder: **Zona Norte (526)**
- **260 chamados** sem bairro associado (id_bairro NULL)

### Parte 2 — Perturbação do Sossego em Grandes Eventos (2022–2024)

- **57.532 chamados** no período total
- Média diária geral: **52,49 chamados/dia**
- Rock in Rio (2ª edição): **139,25 chamados/dia** (+165,3% acima da média)
- Rock in Rio (1ª edição): **133,67 chamados/dia** (+154,6%)
- Carnaval 2023: **63,75 chamados/dia** (+21,4%)
- Réveillon: **50,67 chamados/dia** (−3,5%)

### Parte 3 — Feriados & Clima 2024

- **15 feriados nacionais** em 2024
- Mês com mais feriados: **Novembro (3)**
- **10 feriados** em dias úteis
- Feriado mais aproveitável: **Dia do Trabalhador (01/05)** — 27,3°C, parcialmente nublado

---

## Estrutura do Repositório

```
.
├── analise_sql.sql              # Respostas às questões SQL (BigQuery)
├── analise_python.py            # Questões SQL via Python + basedosdados
├── analise_python.ipynb         # Questões SQL via Python (Jupyter/Colab)
├── analise_api.py               # Questões de API (Feriados + Clima)
├── analise_api.ipynb            # Questões de API (Jupyter/Colab)
├── dashboard.py                 # Dashboard interativo em Streamlit
├── desafio_powerbi_data.xlsx    # Dados estruturados para Power BI
├── requirements.txt             # Dependências Python
└── README.md
```

---

## Dashboard Streamlit

🔗 **Acesse online:** https://bruno-barradas-desafio-casa-civil.streamlit.app

Ou rode localmente:

```bash
cd C:\projetos\desafio-casa-civil
python -m streamlit run dashboard.py
```

| Seção | Conteúdo |
|-------|----------|
| Visão Geral | Métricas consolidadas de todas as análises |
| Chamados 01/04/2023 | Perguntas 1–5 com gráficos interativos |
| Grandes Eventos | Perguntas 6–10, comparativo eventos vs. média geral |
| Feriados & Clima | Perguntas API 1–8, aproveitabilidade de feriados |

> O dashboard funciona com dados reais pré-carregados. Para consultas ao vivo no BigQuery, insira seu GCP Project ID na barra lateral.

---

## Streamlit vs Power BI — qual a diferença?

| Característica | Streamlit | Power BI |
|----------------|-----------|----------|
| **Tecnologia** | Python (código aberto) | Ferramenta Microsoft |
| **Dados SQL** | Pré-carregados ou ao vivo via BigQuery | Importados do Excel estruturado |
| **Dados de Clima/Feriados** | Buscados **ao vivo** nas APIs em tempo real | Fixos no arquivo Excel |
| **Interatividade** | Alta — filtros, gráficos dinâmicos | Alta — filtros, drill-down |
| **Acesso** | Link público via Streamlit Cloud | Power BI Online (conta Microsoft) |
| **Perfil** | Mais técnico — voltado a desenvolvedores | Mais corporativo — voltado a negócios |
| **Atualização** | Automática (APIs ao vivo) | Manual (reimportar Excel) |

> O Streamlit é ideal para compartilhar via link público com dados sempre atualizados. O Power BI é ideal para apresentações corporativas com visual mais profissional.

---

## Power BI

O arquivo `desafio_powerbi_data.xlsx` contém 6 abas estruturadas:

| Aba | Conteúdo |
|-----|----------|
| Resumo Executivo | Todas as respostas consolidadas |
| Chamados por Tipo | Distribuição de tipos em 01/04/2023 |
| Bairros e Subprefeituras | Top 10 bairros + subprefeituras |
| Grandes Eventos | Chamados por evento com variação % |
| Temperatura Mensal | Clima jan–ago 2024 |
| Feriados 2024 | Feriados com dados climáticos |

**Para tela cheia:** publique em [app.powerbi.com](https://app.powerbi.com) e use o ícone de tela cheia no topo.

---

## Como Executar os Scripts

### SQL no BigQuery

1. Acesse [console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)
2. Abra `analise_sql.sql` e execute as queries

### Python localmente

```bash
pip install basedosdados pandas requests plotly streamlit
python analise_python.py
python analise_api.py
```

### Google Colab (sem instalar nada)

1. Acesse [colab.research.google.com](https://colab.research.google.com)
2. Faça upload do `.ipynb` desejado
3. Execute célula por célula

---

## Autenticação GCP

```bash
gcloud auth application-default login
```

---

## Fontes de Dados

| Dado | Origem |
|------|--------|
| Chamados 1746 | `datario.adm_central_atendimento_1746.chamado` |
| Bairros RJ | `datario.dados_mestres.bairro` |
| Eventos | `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` |
| Feriados | [Public Holiday API](https://date.nager.at/Api) |
| Clima histórico | [Open-Meteo](https://open-meteo.com/) |
