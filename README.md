# Desafio Técnico – Analista de Dados
**Escritório de Monitoramento de Projetos e Metas – Secretaria da Casa Civil / Rio de Janeiro**

---

## Estrutura do Repositório

```
.
├── analise_sql.sql          # Respostas às questões SQL (BigQuery)
├── analise_python.ipynb     # Questões SQL via Python + basedosdados (Jupyter/Colab)
├── analise_api.ipynb        # Questões de API (Jupyter/Colab)
├── dashboard.py             # Dashboard interativo em Streamlit
└── README.md
```

---

## Como Executar

### Opção A — Google Colab (recomendado, sem instalar nada)

1. Acesse [colab.research.google.com](https://colab.research.google.com)
2. Faça upload: **Arquivo → Fazer upload de notebook**
3. Na primeira célula: `!pip install basedosdados pandas requests --quiet`
4. Substitua `SEU_PROJECT_ID` pelo seu Project ID do GCP
5. Execute com Shift+Enter ou **Ambiente de execução → Executar tudo**

### Opção B — Jupyter local

```bash
pip install jupyter basedosdados pandas requests plotly streamlit
jupyter notebook
```

### SQL no BigQuery

1. Acesse [console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)
2. Abra `analise_sql.sql` e execute as queries no editor

---

## Dashboard Streamlit

```bash
pip install streamlit pandas requests plotly basedosdados
streamlit run dashboard.py
```

Abre em `http://localhost:8501` com 4 seções:

| Seção | Conteúdo |
|-------|----------|
| Visão Geral | Métricas consolidadas |
| Chamados 01/04/2023 | Perguntas 1–5 com gráficos interativos |
| Grandes Eventos | Perguntas 6–10, comparativo eventos vs. média geral |
| Feriados & Clima | Perguntas API 1–8, aproveitabilidade de feriados |

> O dashboard funciona com dados de demonstração por padrão. Para dados reais, insira seu GCP Project ID na barra lateral.

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
