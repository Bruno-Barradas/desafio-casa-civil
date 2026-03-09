# ============================================================
# DESAFIO TÉCNICO — ANALISTA DE DADOS
# Escritório de Monitoramento — Secretaria da Casa Civil / RJ
# dashboard.py  |  Execute com: streamlit run dashboard.py
# ============================================================

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

try:
    import basedosdados as bd
    BQ_AVAILABLE = True
except ImportError:
    BQ_AVAILABLE = False

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Desafio Técnico — Casa Civil RJ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .metric-card {
    background: #f0f4ff;
    border-radius: 10px;
    padding: 16px 20px;
    border-left: 5px solid #1A3A6B;
    margin-bottom: 8px;
  }
  .metric-card h3 { margin: 0 0 4px 0; font-size: 0.82rem; color: #555; font-weight: 600; }
  .metric-card p  { margin: 0; font-size: 1.9rem; font-weight: 700; color: #1A3A6B; }
  .section-title {
    font-size: 1.05rem; font-weight: 700; color: #1A3A6B;
    margin: 1.4rem 0 0.5rem;
    border-bottom: 2px solid #dce8ff;
    padding-bottom: 4px;
  }
  .analise-box {
    background: #f4f6fa;
    border-left: 5px solid #2E75B6;
    border-radius: 6px;
    padding: 14px 18px;
    margin: 10px 0 16px 0;
    font-size: 0.95rem;
    color: #333;
  }
  .analise-box strong { color: #1A3A6B; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/"
        "Brasão_do_Rio_de_Janeiro.svg/180px-Brasão_do_Rio_de_Janeiro.svg.png",
        width=72,
    )
    st.title("Painel de Análise")
    st.caption("Desafio Técnico — Analista de Dados\nSecretaria da Casa Civil / RJ")
    st.markdown("---")

    pagina = st.radio(
        "Navegação",
        [
            "🏠 Apresentação",
            "📞 Chamados 01/04/2023",
            "🎉 Perturbação do Sossego",
            "🏖️ Feriados & Clima 2024",
            "💡 Insights Adicionais",
            "✅ Recomendações",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if BQ_AVAILABLE:
        billing_id = st.text_input(
            "GCP Billing Project ID",
            placeholder="seu-project-id",
            help="Necessário para consultar o BigQuery ao vivo",
        )
    else:
        st.warning("basedosdados não instalado.\npip install basedosdados")
        billing_id = None

    st.markdown("---")
    st.caption("Fontes: datario · date.nager.at · open-meteo.com")


# ============================================================
# HELPERS
# ============================================================
def metric_card(title, value):
    st.markdown(
        f'<div class="metric-card"><h3>{title}</h3><p>{value}</p></div>',
        unsafe_allow_html=True,
    )

def analise(texto):
    st.markdown(
        f'<div class="analise-box"><strong>Análise e Recomendação:</strong> {texto}</div>',
        unsafe_allow_html=True,
    )

def run_query(sql):
    if not BQ_AVAILABLE or not billing_id:
        return None
    try:
        return bd.read_sql(sql, billing_project_id=billing_id)
    except Exception as e:
        st.error(f"Erro BigQuery: {e}")
        return None

WMO = {
    0: "Céu limpo", 1: "Principalmente limpo", 2: "Parcialmente nublado",
    3: "Totalmente nublado", 45: "Nevoeiro", 48: "Nevoeiro c/ geada",
    51: "Garoa leve", 53: "Garoa moderada", 55: "Garoa intensa",
    61: "Chuva leve", 63: "Chuva moderada", 65: "Chuva intensa",
    80: "Pancadas leves", 81: "Pancadas moderadas", 82: "Pancadas intensas",
    95: "Trovoada", 96: "Trovoada c/ granizo", 99: "Trovoada intensa",
}
BAD_CODES = {3,45,48,51,53,55,61,63,65,71,73,75,77,80,81,82,85,86,95,96,99}

def wmo_label(code):
    if pd.isna(code):
        return "Sem dados"
    return WMO.get(int(code), f"Código {int(code)}")

AZUL  = "#1A3A6B"
AZUL2 = "#2E75B6"
VERM  = "#C0392B"
CINZA = "#7f8c8d"

# ============================================================
# DADOS PRÉ-CALCULADOS (idênticos ao v5)
# ============================================================
DADOS_CHAMADOS_TIPO = pd.DataFrame({
    "tipo": ["Outros (sem categoria)", "Estacionamento irregular",
              "Perturbação do Sossego", "Iluminação Pública",
              "Coleta de Lixo", "Demais tipos"],
    "total": [653, 373, 310, 245, 198, 288],
})

DADOS_BAIRROS = pd.DataFrame({
    "bairro": ["Campo Grande", "Tijuca", "Barra da Tijuca"],
    "chamados": [125, 100, 62],
    "pct": ["6,0%", "4,8%", "3,0%"],
})

DADOS_SUBPREF = pd.DataFrame({
    "subprefeitura": ["Zona Norte", "Zona Oeste", "Zona Sul",
                      "Centro", "Barra e Jacarepaguá", "Sem bairro associado"],
    "chamados": [526, 480, 310, 180, 150, 260],
    "pct": ["27,6%", "25,2%", "16,3%", "9,4%", "7,9%", "13,6%"],
})

DADOS_EVENTOS = pd.DataFrame({
    "evento": [
        "Rock in Rio (2ª edição)", "Rock in Rio (1ª edição)",
        "Rock in Rio (combinado)", "Carnaval 2023", "Réveillon 2022/2023"
    ],
    "periodo": [
        "08–11/09/2022", "02–04/09/2022",
        "Set/2022", "18–21/02/2023", "30/12/2022–01/01/2023"
    ],
    "duracao": [4, 3, 7, 4, 3],
    "total": [557, 401, 958, 255, 152],
    "media_diaria": [139.25, 133.67, 136.86, 63.75, 50.67],
    "variacao": ["+165,3%", "+154,6%", "+160,7%", "+21,4%", "−3,5%"],
})

DADOS_TEMP = pd.DataFrame({
    "mes": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago"],
    "mes_num": [1, 2, 3, 4, 5, 6, 7, 8],
    "temp": [26.1, 27.1, 26.5, 25.2, 23.8, 21.4, 20.8, 21.9],
})

MEDIA_GERAL = 52.49


# ============================================================
# PÁGINA: APRESENTAÇÃO
# ============================================================
if pagina == "🏠 Apresentação":
    st.title("Desafio Técnico — Analista de Dados")
    st.subheader("Escritório de Monitoramento de Projetos e Metas\nSecretaria da Casa Civil — Prefeitura do Rio de Janeiro")
    st.caption("Fevereiro de 2026")
    st.markdown("---")

    st.markdown("""
Este dashboard apresenta a solução desenvolvida para o Desafio Técnico do processo seletivo
para a vaga de Analista de Dados do Escritório de Monitoramento de Projetos e Metas,
vinculado à Secretaria da Casa Civil da Prefeitura do Rio de Janeiro.

O desafio foi estruturado em **três partes independentes**:
- A primeira consiste na análise dos chamados registrados no Sistema 1746 no dia 01 de abril de 2023, com foco na distribuição geográfica e por tipo de serviço.
- A segunda examina o comportamento dos chamados de perturbação do sossego durante grandes eventos realizados na cidade entre 2022 e 2024.
- A terceira parte integra dados de APIs públicas para caracterizar os feriados nacionais de 2024 sob o ponto de vista climático.

Todas as análises foram realizadas com dados reais obtidos diretamente do Google BigQuery,
por meio do projeto público **datario** disponibilizado pela Base dos Dados, e de duas APIs públicas:
a Public Holiday API (date.nager.at) para os feriados nacionais e a Open-Meteo Historical Weather API
para os dados climáticos históricos do Rio de Janeiro.

A análise foi conduzida com ênfase na qualidade dos dados, na contextualização de cada resultado
e na geração de recomendações acionáveis com base exclusivamente no que os dados permitem afirmar.
Onde os dados apresentam limitações, essas limitações são indicadas de forma explícita.
    """)

    st.markdown("---")
    st.markdown("### Sumário Executivo")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Chamados em 01/04/2023", "2.067")
    with c2:
        metric_card("Perturbação do Sossego (2022–2024)", "57.532")
    with c3:
        metric_card("Média diária do período", "52,49/dia")
    with c4:
        metric_card("Feriados nacionais em 2024", "15")

    st.markdown("---")
    st.markdown("### Os 5 Findings Principais")

    findings = [
        ("🔴 Alto", "Rock in Rio gerou +165,3% de reclamações de barulho vs. média diária de 3 anos",
         "Protocolo preventivo de fiscalização para períodos de evento"),
        ("🔴 Alto", "31% dos chamados de 01/04/2023 sem categoria — maior grupo do dia",
         "Revisão do formulário de registro com categoria obrigatória"),
        ("🔴 Alto", "12,6% dos chamados do dia sem localização geográfica válida",
         "Validação de endereço obrigatória no momento do registro"),
        ("🟡 Médio", "Réveillon 2022/2023 foi o único evento com média diária abaixo da média geral do período",
         "Investigar o comportamento atípico com dados complementares"),
        ("🟢 Baixo", "Rio de Janeiro não registrou temperatura abaixo de 20°C em nenhum mês de 2024",
         "Dado relevante para planejamento de eventos e turismo de inverno"),
    ]

    for impacto, finding, recomendacao in findings:
        with st.expander(f"{impacto} — {finding}"):
            st.write(f"**Recomendação:** {recomendacao}")

    st.markdown("---")
    st.markdown(
        '<div class="analise-box"><strong>Conclusão executiva:</strong> '
        'Os dados revelam dois problemas estruturais simultâneos. O primeiro é de demanda: grandes eventos '
        'amplificam a procura por fiscalização de forma previsível, o que tornaria viável um protocolo '
        'de reforço antecipado. O segundo é de qualidade de dados: com 31% dos chamados sem categoria '
        'e 12,6% sem localização, a capacidade de análise e de roteamento automático dos chamados fica '
        'significativamente comprometida. Ambos os problemas são corrigíveis com ações específicas e de '
        'complexidade moderada.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Limitações dos Dados")
    st.info(
        "• Os dados detalhados de chamados cobrem apenas o dia 01/04/2023 para a Parte 1. "
        "Não é possível afirmar se os padrões desse dia são representativos de outros dias do ano.\n\n"
        "• Os dados de perturbação do sossego cobrem 2022–2024, mas sem localização geográfica dos "
        "chamados durante os eventos, o que impede confirmar em quais bairros as reclamações se concentraram.\n\n"
        "• Os dados climáticos cobrem apenas janeiro a agosto de 2024. "
        "Os feriados de setembro a dezembro não possuem dados de clima associados.\n\n"
        "• Os dados não incluem informações de população por bairro ou subprefeitura, "
        "o que impede análises per capita diretas."
    )


# ============================================================
# PÁGINA: CHAMADOS 01/04/2023
# ============================================================
elif pagina == "📞 Chamados 01/04/2023":
    st.title("📞 Chamados do 1746 — 01/04/2023")
    st.markdown(
        "Análise de todos os chamados de serviços públicos abertos no sistema 1746 da Prefeitura "
        "do Rio de Janeiro no dia 01 de abril de 2023, cruzando com a tabela de bairros para "
        "identificar padrões geográficos."
    )
    st.markdown("---")

    # Busca BQ ou usa dados pré-calculados
    if BQ_AVAILABLE and billing_id:
        with st.spinner("Consultando BigQuery..."):
            df_tipo = run_query("""
                SELECT tipo, COUNT(*) AS total_chamados
                FROM `datario.adm_central_atendimento_1746.chamado`
                WHERE DATE(data_inicio) = '2023-04-01'
                GROUP BY tipo ORDER BY total_chamados DESC LIMIT 15
            """)
            df_bairros = run_query("""
                SELECT b.nome AS bairro, COUNT(*) AS total_chamados
                FROM `datario.adm_central_atendimento_1746.chamado` c
                JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
                WHERE DATE(c.data_inicio) = '2023-04-01'
                GROUP BY bairro ORDER BY total_chamados DESC LIMIT 15
            """)
            df_subpref = run_query("""
                SELECT b.subprefeitura, COUNT(*) AS total_chamados
                FROM `datario.adm_central_atendimento_1746.chamado` c
                JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
                WHERE DATE(c.data_inicio) = '2023-04-01'
                GROUP BY b.subprefeitura ORDER BY total_chamados DESC
            """)
    else:
        df_tipo    = DADOS_CHAMADOS_TIPO.rename(columns={"total": "total_chamados"})
        df_bairros = DADOS_BAIRROS.rename(columns={"chamados": "total_chamados"})
        df_subpref = DADOS_SUBPREF.rename(columns={"chamados": "total_chamados"})

    # ── Finding 1.1 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 1.1 — Volume total: 2.067 chamados em um único dia</p>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Total de chamados em 01/04/2023", "2.067")
    with c2:
        metric_card("Média por hora", "86 chamados/hora")
    with c3:
        metric_card("Frequência equivalente", "1,4 chamados/minuto")

    st.markdown(
        "Em 01 de abril de 2023, o sistema 1746 registrou 2.067 solicitações de serviços públicos "
        "em um único dia. Esse número representa a demanda bruta de atendimento que a Prefeitura "
        "precisou absorver naquele dia."
    )
    analise(
        "2.067 chamados em um dia significa que, se a Prefeitura tivesse uma equipe dedicada com "
        "jornada de 8 horas, cada operador precisaria processar um chamado a cada 7 minutos sem pausa. "
        "Isso indica que sistemas de triagem automática e priorização por urgência e localização são "
        "necessários para tornar o atendimento viável. O que os dados não permitem avaliar: quantos "
        "desses chamados foram efetivamente atendidos e em qual prazo."
    )
    st.markdown("---")

    # ── Finding 1.2 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 1.2 — Tipo mais frequente: Estacionamento irregular (18%)</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = px.bar(
            df_tipo.sort_values("total_chamados"),
            x="total_chamados", y="tipo" if "tipo" in df_tipo.columns else df_tipo.columns[0],
            orientation="h",
            color="total_chamados",
            color_continuous_scale=[[0, "#dce8ff"], [1, AZUL]],
            labels={"total_chamados": "Chamados", "tipo": ""},
            text="total_chamados",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.dataframe(
            DADOS_CHAMADOS_TIPO.rename(columns={"tipo": "Tipo de Chamado", "total": "Total"}),
            use_container_width=True, hide_index=True,
        )
        st.markdown(
            "Estacionamento irregular foi o tipo específico mais registrado, com **373 ocorrências** "
            "(18% dos chamados). A categoria **Outros** lidera com 653 chamados (31,6%) — "
            "mais que qualquer tipo específico."
        )

    analise(
        "Estacionamento irregular como principal demanda indica que a fiscalização de trânsito foi "
        "a necessidade mais expressa pelo cidadão naquele dia. Os dados não incluem horário nem "
        "localização específica dos chamados dentro dos bairros. Para transformar esse resultado em ação, "
        "seria necessário cruzar com o horário de abertura e o logradouro do chamado. "
        "Nota crítica: a categoria 'Outros' soma 653 chamados, mais que qualquer tipo específico. "
        "31,6% dos chamados sem classificação adequada é o problema mais grave de qualidade de dados deste conjunto."
    )
    st.markdown("---")

    # ── Finding 1.3 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 1.3 — Top 3 bairros por volume de chamados</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig2 = px.bar(
            DADOS_BAIRROS.sort_values("chamados", ascending=True),
            x="chamados", y="bairro",
            orientation="h",
            color="chamados",
            color_continuous_scale=[[0, "#dce8ff"], [1, AZUL2]],
            text="chamados",
            labels={"chamados": "Chamados", "bairro": ""},
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, coloraxis_showscale=False, height=260)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.dataframe(
            DADOS_BAIRROS.rename(columns={"bairro": "Bairro", "chamados": "Chamados", "pct": "% do Total"}),
            use_container_width=True, hide_index=True,
        )

    analise(
        "O volume absoluto de chamados por bairro é um dado importante, mas incompleto sem contexto "
        "populacional. Campo Grande tem aproximadamente 500 mil habitantes; Tijuca tem cerca de 150 mil. "
        "Proporcionalmente, Tijuca registrou 1 chamado para cada 1.500 habitantes, enquanto Campo Grande "
        "registrou 1 para cada 4.000 habitantes, o que inverte a leitura. Tijuca apresenta, "
        "proporcionalmente, maior pressão sobre os serviços públicos. Para uma alocação equitativa de "
        "recursos, a Prefeitura deveria trabalhar com chamados per capita, não com volume absoluto. "
        "Os dados populacionais necessários para essa análise em todos os bairros não fazem parte do "
        "dataset deste desafio."
    )
    st.markdown("---")

    # ── Finding 1.4 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 1.4 — Chamados por Subprefeitura em 01/04/2023</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        df_sp_plot = DADOS_SUBPREF.copy()
        cores = [AZUL if s != "Sem bairro associado" else CINZA for s in df_sp_plot["subprefeitura"]]
        fig3 = px.bar(
            df_sp_plot.sort_values("chamados", ascending=True),
            x="chamados", y="subprefeitura",
            orientation="h",
            text="chamados",
            labels={"chamados": "Chamados", "subprefeitura": ""},
            color="subprefeitura",
            color_discrete_sequence=[AZUL, AZUL2, "#4472C4", "#70AD47", "#ED7D31", CINZA],
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(showlegend=False, height=360)
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.dataframe(
            DADOS_SUBPREF.rename(columns={
                "subprefeitura": "Subprefeitura",
                "chamados": "Chamados",
                "pct": "% do Total"
            }),
            use_container_width=True, hide_index=True,
        )

    st.markdown(
        "A Subprefeitura da Zona Norte concentrou 526 chamados (27,6% do total com localização). "
        "A Zona Oeste ficou em segundo com 480 (25,2%), seguida pela Zona Sul com 310 (16,3%), "
        "Centro com 180 (9,4%) e Barra e Jacarepaguá com 150 (7,9%). "
        "Os 260 chamados sem bairro associado (13,6%) não puderam ser alocados em nenhuma subprefeitura."
    )
    analise(
        "A Zona Norte e a Zona Oeste juntas responderam por mais da metade (52,8%) de todos os chamados "
        "com localização identificada no dia. Essa concentração é coerente com o fato de essas duas "
        "regiões abrigarem a maior parcela da população do município. Sem dados populacionais por "
        "subprefeitura, não é possível afirmar se essa proporção reflete maior carência de serviços "
        "ou simplesmente maior volume demográfico. Uma análise per capita seria necessária para definir "
        "prioridades de alocação de recursos com maior precisão."
    )
    st.markdown("---")

    # ── Finding 1.5 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 1.5 — 260 chamados sem localização (12,6% do total)</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 3])
    with col_a:
        fig4 = px.pie(
            values=[1807, 260],
            names=["Com localização (1.807)", "Sem localização (260)"],
            color_discrete_sequence=[AZUL, VERM],
            hole=0.5,
        )
        fig4.update_layout(height=280)
        st.plotly_chart(fig4, use_container_width=True)

    with col_b:
        st.dataframe(pd.DataFrame({
            "Indicador": [
                "Chamados sem id_bairro válido em 01/04/2023",
                "Percentual do total do dia",
                "Tipos predominantes",
            ],
            "Valor": [
                "260 chamados",
                "12,6% (1 em cada 8 chamados)",
                "Atendimento Social, Cartão Família Carioca, Alvará",
            ]
        }), use_container_width=True, hide_index=True)

        st.markdown(
            "De 2.067 chamados abertos em 01/04/2023, 260 não possuem id_bairro válido na tabela "
            "de bairros do município. Chamados sem localização não podem ser cruzados com dados "
            "geográficos e não contribuem para o planejamento territorial de serviços."
        )

    analise(
        "12,6% de registros sem localização válida em um sistema que é fundamentalmente geográfico "
        "representa uma lacuna que compromete toda análise territorial. A recomendação é implementar "
        "validação de endereço obrigatória no formulário de registro do 1746, com campo de CEP ou "
        "logradouro como obrigatório. Ação sugerida: auditoria nos chamados do tipo 'Outros' e 'Atendimento Social' para determinar quais deveriam ter localização e quais são genuinamente sem endereço."
    )


# ============================================================
# PÁGINA: PERTURBAÇÃO DO SOSSEGO
# ============================================================
elif pagina == "🎉 Perturbação do Sossego":
    st.title("🎉 Perturbação do Sossego em Grandes Eventos (2022–2024)")
    st.markdown(
        "Análise dos chamados do subtipo 5071 (Perturbação do sossego) no período de 01/01/2022 "
        "a 31/12/2024, cruzados com as datas dos eventos Réveillon, Carnaval e Rock in Rio "
        "registrados na tabela de ocupação hoteleira."
    )
    st.markdown("---")

    # ── Finding 2.1 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 2.1 — 57.532 chamados em 3 anos: uma reclamação de barulho a cada 27 minutos</p>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total chamados (2022–2024)", "57.532")
    with c2:
        metric_card("Total de dias no período", "1.096 dias")
    with c3:
        metric_card("Média diária do período", "52,49/dia")
    with c4:
        metric_card("Frequência equivalente", "1 a cada 27 min")

    st.markdown(
        "Entre 01 de janeiro de 2022 e 31 de dezembro de 2024, foram registrados 57.532 chamados "
        "de perturbação do sossego no sistema 1746. A média resultante de **52,49 chamados por dia** "
        "é a referência utilizada para avaliar o impacto de cada evento: qualquer evento com média "
        "diária superior a 52,49 está gerando um volume de reclamações acima do padrão habitual da cidade."
    )
    analise(
        "O volume de 57.532 chamados de perturbação do sossego em três anos demonstra que esse tipo "
        "de demanda é contínuo e expressivo, não se concentrando apenas em períodos de eventos. "
        "A média de 52,49 chamados por dia justifica a existência de uma estrutura permanente de "
        "fiscalização de barulho, e não apenas reforços pontuais durante eventos específicos."
    )
    st.markdown("---")

    # ── Finding 2.2 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 2.2 — Rock in Rio: +165,3% acima da média diária de 3 anos</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Gráfico média diária com linha de base
        df_ev_plot = DADOS_EVENTOS[DADOS_EVENTOS["evento"] != "Rock in Rio (combinado)"].copy()
        cores_ev = [VERM if v > 0 else AZUL2
                    for v in [139.25, 133.67, 63.75, 50.67]]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_ev_plot["evento"],
            y=df_ev_plot["media_diaria"],
            text=df_ev_plot["media_diaria"],
            texttemplate="%{text:.2f}",
            textposition="outside",
            marker_color=[VERM, VERM, AZUL2, AZUL2],
        ))
        fig.add_hline(
            y=MEDIA_GERAL, line_dash="dash", line_color="gray",
            annotation_text=f"Média geral do período: {MEDIA_GERAL}/dia",
            annotation_position="top right",
        )
        fig.update_layout(
            title="Média Diária de Chamados por Evento vs. Média Geral",
            yaxis_title="Chamados/dia",
            xaxis_title="",
            height=400,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.dataframe(
            DADOS_EVENTOS.rename(columns={
                "evento": "Evento", "periodo": "Período",
                "duracao": "Duração (dias)", "total": "Total Chamados",
                "media_diaria": "Média/Dia", "variacao": "vs. Média Geral"
            }),
            use_container_width=True, hide_index=True,
        )

    st.markdown(
        "A segunda edição do Rock in Rio 2022 registrou **139,25 chamados por dia**, "
        "165,3% acima da média diária de 52,49 do período completo de 3 anos. "
        "Combinando as duas edições do Rock in Rio 2022, o total chega a **958 chamados em 7 dias**."
    )
    analise(
        "O Rock in Rio é um evento recorrente com datas divulgadas com antecedência. O aumento de "
        "+165,3% nas reclamações de barulho indica que a demanda por fiscalização é 2,65 vezes maior "
        "que o padrão habitual. Esse comportamento previsível torna viável um protocolo de reforço "
        "preventivo das equipes de fiscalização especificamente para o período do evento. Os dados "
        "não incluem a localização geográfica dos chamados durante o Rock in Rio, o que impede "
        "confirmar se a concentração é na Barra da Tijuca ou distribuída pela cidade. Esse "
        "cruzamento seria o próximo passo investigativo."
    )
    st.markdown("---")

    # ── Finding 2.3 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 2.3 — Réveillon 2022/2023: o único evento com média abaixo do padrão habitual</p>',
                unsafe_allow_html=True)

    st.markdown(
        "O Réveillon 2022/2023 registrou uma média de **50,67 chamados de perturbação do sossego "
        "por dia**, durante seus 3 dias de realização. Para comparar os eventos de forma justa, "
        "independentemente de sua duração, a análise utiliza a **média diária de cada evento** e "
        "compara com a **média diária do período completo de 3 anos**, que foi de **52,49 chamados "
        "por dia**. Ou seja: um dia comum qualquer entre 2022 e 2024 gerou, em média, mais "
        "reclamações de barulho do que cada dia do Réveillon. A diferença é de 1,82 chamado a menos "
        "por dia, equivalente a 3,5% abaixo do padrão habitual da cidade. O Réveillon foi o único "
        "dos eventos analisados com média diária inferior à média geral do período."
    )
    analise(
        "Este é o finding mais contraintuitivo do projeto. O Réveillon de Copacabana é um dos "
        "maiores eventos de rua do mundo, atraindo cerca de 2 milhões de pessoas. A expectativa "
        "seria um pico nas reclamações de barulho, e os dados mostram o contrário. Os dados "
        "disponíveis não permitem explicar esse fenômeno. Para entender a causa, seriam necessários: "
        "(1) o volume total de ligações recebidas pelo 1746 no período para verificar se houve "
        "sobrecarga das linhas; (2) a distribuição geográfica dos chamados para verificar se "
        "Copacabana especificamente teve redução; (3) dados de outros anos de Réveillon para "
        "confirmar se é um padrão ou uma exceção de 2022/2023."
    )
    st.markdown("---")

    # ── Finding 2.4 ──────────────────────────────────────────
    st.markdown('<p class="section-title">Finding 2.4 — Carnaval 2023: +21,4%, significativamente menor que o Rock in Rio</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 3])
    with col_a:
        metric_card("Carnaval 2023 — Média diária", "63,75/dia")
        metric_card("Variação vs. média geral", "+21,4%")
        metric_card("Comparado ao Rock in Rio", "2,15x menor")

    with col_b:
        st.markdown(
            "O Carnaval 2023 gerou uma média de 63,75 chamados de perturbação do sossego por dia, "
            "21,4% acima da média geral de 52,49. O aumento é real e estatisticamente relevante, "
            "mas representa uma intensidade significativamente menor que a observada durante o "
            "Rock in Rio, que superou a média em 165,3%."
        )
        analise(
            "A diferença entre os dois eventos é expressiva: o Rock in Rio gerou uma média diária "
            "mais de seis vezes maior que o acréscimo observado no Carnaval. Os dados não permitem "
            "explicar essa disparidade com certeza, pois não há localização geográfica dos chamados "
            "durante os eventos nem dados de outros anos de Carnaval para confirmar o padrão. "
            "Uma possível explicação é que o Carnaval de rua distribui o barulho por toda a cidade, "
            "diluindo as reclamações por bairro, enquanto o Rock in Rio concentra o impacto sonoro "
            "em uma região específica. Essa hipótese precisaria ser testada com dados geográficos."
        )


# ============================================================
# PÁGINA: FERIADOS & CLIMA 2024
# ============================================================
elif pagina == "🏖️ Feriados & Clima 2024":
    st.title("🏖️ Feriados Nacionais e Clima no Rio de Janeiro — 2024")
    st.caption("Dados: Public Holiday API (date.nager.at) · Open-Meteo Historical Weather API")
    st.markdown(
        "Integração de dados de duas APIs públicas: feriados nacionais (date.nager.at) e clima "
        "histórico diário do Rio de Janeiro (open-meteo.com). Os dados climáticos cobrem "
        "janeiro a agosto de 2024."
    )
    st.markdown("---")

    @st.cache_data(show_spinner="Buscando feriados...")
    def fetch_holidays():
        r = requests.get("https://date.nager.at/api/v3/PublicHolidays/2024/BR", timeout=10)
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        df["date"]        = pd.to_datetime(df["date"])
        df["weekday"]     = df["date"].dt.day_name()
        df["weekday_num"] = df["date"].dt.dayofweek
        df["month"]       = df["date"].dt.month
        return df

    @st.cache_data(show_spinner="Buscando dados climáticos...")
    def fetch_weather():
        r = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": -22.9068, "longitude": -43.1729,
                "start_date": "2024-01-01", "end_date": "2024-08-01",
                "daily": ["temperature_2m_mean", "weathercode"],
                "timezone": "America/Sao_Paulo",
            },
            timeout=15,
        )
        r.raise_for_status()
        df = pd.DataFrame(r.json()["daily"])
        df["time"] = pd.to_datetime(df["time"])
        df = df.rename(columns={"time": "date", "temperature_2m_mean": "temp_mean", "weathercode": "weather_code"})
        df["month"] = df["date"].dt.month
        return df

    try:
        holidays = fetch_holidays()
        weather  = fetch_weather()
        api_ok   = True
    except Exception as e:
        st.error(f"Erro ao buscar APIs: {e}")
        api_ok = False

    if api_ok:
        holidays_period = holidays[holidays["date"] <= pd.Timestamp("2024-08-01")].copy()
        h_weather = holidays_period.merge(
            weather[["date", "temp_mean", "weather_code"]], on="date", how="left"
        )
        h_weather["descricao_tempo"] = h_weather["weather_code"].apply(wmo_label)
        h_weather["aproveitavel"] = h_weather.apply(
            lambda r: (r["temp_mean"] >= 20 and int(r["weather_code"]) not in BAD_CODES)
                      if pd.notna(r["temp_mean"]) and pd.notna(r["weather_code"]) else None,
            axis=1,
        )

        # ── Finding 3.1 ──────────────────────────────────────
        st.markdown('<p class="section-title">Finding 3.1 — 15 feriados em 2024: 10 em dias úteis (67%)</p>',
                    unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Feriados nacionais em 2024", str(len(holidays)))
        with c2:
            uteis = int((holidays["weekday_num"] < 5).sum())
            metric_card("Em dias úteis", f"{uteis} (66,7%)")
        with c3:
            metric_card("Em fins de semana", f"{len(holidays) - uteis} (33,3%)")
        with c4:
            metric_card("Mês com mais feriados", "Novembro (3)")

        col_a, col_b = st.columns(2)
        with col_a:
            by_month = holidays.groupby("month").size().reset_index(name="qtd")
            by_month["mes"] = by_month["month"].apply(lambda m: date(2024, m, 1).strftime("%b"))
            fig = px.bar(
                by_month, x="mes", y="qtd",
                color="qtd", color_continuous_scale=[[0, "#dce8ff"], [1, AZUL]],
                text="qtd", labels={"qtd": "Feriados", "mes": "Mês"},
                title="Feriados por Mês em 2024",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=320)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            dias_pt = {
                "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
                "Thursday": "Quinta", "Friday": "Sexta",
                "Saturday": "Sábado", "Sunday": "Domingo",
            }
            by_day = holidays.copy()
            by_day["dia_pt"] = by_day["weekday"].map(dias_pt)
            by_day_count = by_day.groupby("dia_pt").size().reset_index(name="qtd")
            fig2 = px.pie(
                by_day_count, names="dia_pt", values="qtd",
                hole=0.4,
                color_discrete_sequence=[AZUL, AZUL2, "#4472C4", "#70AD47", "#ED7D31", VERM, CINZA],
                title="Feriados por Dia da Semana",
            )
            fig2.update_layout(height=320)
            st.plotly_chart(fig2, use_container_width=True)

        analise(
            "10 dos 15 feriados nacionais de 2024 retiram efetivamente um dia útil do calendário "
            "de trabalho. Novembro concentra 3 feriados em menos de três semanas, sendo 2 em dias úteis. "
            "Para a gestão da Prefeitura, isso implica planejamento antecipado de escalas de plantão "
            "para os 10 feriados úteis e comunicação prévia ao cidadão sobre serviços suspensos, "
            "uma vez que serviços de saúde, segurança e atendimento de urgência não são interrompidos nesses períodos."
        )
        st.markdown("---")

        # ── Finding 3.2 ──────────────────────────────────────
        st.markdown('<p class="section-title">Finding 3.2 — Temperatura mensal: fevereiro é o mês mais quente (27,1°C)</p>',
                    unsafe_allow_html=True)

        monthly_temp = weather.groupby("month")["temp_mean"].mean().round(2).reset_index()
        monthly_temp["mes"] = monthly_temp["month"].apply(lambda m: date(2024, m, 1).strftime("%b"))

        col_a, col_b = st.columns([3, 2])
        with col_a:
            fig3 = px.line(
                monthly_temp, x="mes", y="temp_mean",
                markers=True, text="temp_mean",
                color_discrete_sequence=[VERM],
                labels={"temp_mean": "Temp. Média (°C)", "mes": "Mês"},
                title="Temperatura Média Mensal — Rio de Janeiro (jan–ago 2024)",
            )
            fig3.add_hline(y=20, line_dash="dash", line_color=AZUL2,
                           annotation_text="Limiar 'frio' carioca (20°C)")
            fig3.update_traces(texttemplate="%{text:.1f}°C", textposition="top center")
            fig3.update_layout(height=360, yaxis_range=[18, 29])
            st.plotly_chart(fig3, use_container_width=True)

        with col_b:
            st.dataframe(
                DADOS_TEMP.rename(columns={"mes": "Mês", "temp": "Temp. Média (°C)"})[["Mês", "Temp. Média (°C)"]],
                use_container_width=True, hide_index=True,
            )
            st.markdown(
                "Fevereiro de 2024 registrou temperatura média de **27,1°C**, o valor mais alto dos "
                "oito meses analisados. Julho foi o mês mais frio com **20,8°C**, exatamente no "
                "limite do critério de 'frio' carioca (abaixo de 20°C). Nenhum mês atingiu esse limiar."
            )

        analise(
            "Fevereiro é simultaneamente o mês mais quente e o período em que o Carnaval frequentemente "
            "ocorre. Temperatura de 27,1°C combinada com grandes aglomerações representa risco de "
            "desidratação e maior demanda por serviços de saúde. Recomenda-se reforço de postos de "
            "hidratação e atendimento médico especificamente em fevereiro. Os dados de 2024 não "
            "permitem afirmar se esse é um padrão histórico estável, sendo necessário comparar com "
            "séries climáticas de anos anteriores para confirmar a tendência."
        )
        st.markdown("---")

        # ── Finding 3.3 ──────────────────────────────────────
        st.markdown('<p class="section-title">Finding 3.3 — Feriado mais aproveitável: Dia do Trabalhador (27,3°C, céu limpo)</p>',
                    unsafe_allow_html=True)

        st.markdown("""
**Critérios para feriado aproveitável:**
- 🌡️ Temperatura média **≥ 20°C** (carioca não vai à praia com frio)
- ☀️ Tempo **sem** chuva, céu totalmente nublado, nevoeiro ou tempestade
        """)

        h_show = h_weather.copy()
        h_show["status"] = h_show["aproveitavel"].map(
            {True: "✅ Aproveitável", False: "❌ Não aproveitável", None: "❓ Sem dados"}
        )

        fig4 = px.bar(
            h_show, x="localName", y="temp_mean",
            color="status",
            color_discrete_map={
                "✅ Aproveitável": "#27ae60",
                "❌ Não aproveitável": VERM,
                "❓ Sem dados": CINZA,
            },
            text="temp_mean",
            labels={"temp_mean": "Temp. Média (°C)", "localName": "Feriado"},
            title="Temperatura e Aproveitabilidade por Feriado (jan–ago 2024)",
        )
        fig4.add_hline(y=20, line_dash="dash", line_color=AZUL2, annotation_text="20°C (limiar frio)")
        fig4.update_traces(texttemplate="%{text:.1f}°C", textposition="outside")
        fig4.update_layout(xaxis_tickangle=-25, height=420)
        st.plotly_chart(fig4, use_container_width=True)

        # Melhor feriado
        aprov_df = h_weather[h_weather["aproveitavel"] == True].copy()
        if len(aprov_df) > 0:
            aprov_df["score"] = aprov_df["temp_mean"] - aprov_df["weather_code"] * 2
            melhor = aprov_df.sort_values("score", ascending=False).iloc[0]
            st.success(
                f"🏆 **Feriado mais aproveitável:** {melhor['localName']} "
                f"({melhor['date'].strftime('%d/%m/%Y')}, {melhor['weekday']}) — "
                f"{melhor['temp_mean']}°C · {melhor['descricao_tempo']}"
            )

        st.markdown(
            "Nenhum feriado no período analisado registrou temperatura média abaixo de 20°C. "
            "O critério de 'frio' nunca foi ativado. O fator determinante para a não "
            "aproveitabilidade dos feriados foi exclusivamente a condição climática, "
            "seja céu totalmente encoberto ou presença de chuva."
        )
        analise(
            "O Dia do Trabalhador (01/05/2024, quarta-feira) foi o feriado climaticamente mais "
            "favorável: 27,3°C e céu principalmente limpo. Porém caiu em uma quarta-feira, sem "
            "criar um feriado prolongado. Isso ilustra que o melhor feriado climaticamente não é "
            "necessariamente o mais aproveitado, pois o dia da semana influencia diretamente o "
            "comportamento do cidadão. Uma análise completa exigiria dados de frequência em praias "
            "e parques, que não estão disponíveis neste conjunto de dados."
        )

        st.markdown("---")
        h_show["date"] = h_show["date"].dt.strftime("%d/%m/%Y")
        st.markdown('<p class="section-title">Detalhes por Feriado (jan–ago 2024)</p>', unsafe_allow_html=True)
        st.dataframe(
            h_show[["date", "localName", "weekday", "temp_mean", "weather_code", "descricao_tempo", "status"]].rename(columns={
                "date": "Data", "localName": "Feriado", "weekday": "Dia",
                "temp_mean": "Temp. (°C)", "weather_code": "Cód. WMO",
                "descricao_tempo": "Condição", "status": "Aproveitável?"
            }),
            use_container_width=True, hide_index=True,
        )


# ============================================================
# PÁGINA: INSIGHTS ADICIONAIS
# ============================================================
elif pagina == "💡 Insights Adicionais":
    st.title("💡 Insights Adicionais")
    st.markdown(
        "Análises que vão além das perguntas formuladas no desafio, identificando padrões e "
        "anomalias que os dados revelam quando observados em conjunto."
    )
    st.markdown("---")

    # ── Insight A ────────────────────────────────────────────
    st.markdown('<p class="section-title">Insight A — "Outros" é o maior problema de qualidade de dados</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = px.bar(
            DADOS_CHAMADOS_TIPO.sort_values("total"),
            x="total", y="tipo", orientation="h",
            color=DADOS_CHAMADOS_TIPO.sort_values("total")["tipo"].apply(
                lambda x: "⚠️ Sem categoria" if x == "Outros (sem categoria)" else "Categorizado"
            ),
            color_discrete_map={"⚠️ Sem categoria": VERM, "Categorizado": AZUL},
            text="total",
            labels={"total": "Chamados", "tipo": ""},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=True, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown(
            "653 dos 2.067 chamados de 01/04/2023 foram registrados como 'Outros', sem tipo "
            "específico. Isso representa **31,6% do total**, mais que qualquer categoria definida "
            "incluindo Estacionamento irregular (373 chamados, 18%)."
        )
        analise(
            "Ter 31% dos chamados sem classificação é ter 31% das ordens de serviço sem destino "
            "definido. Esses chamados não podem ser roteados automaticamente ao departamento correto, "
            "não entram nas estatísticas de tipos de problema e não geram aprendizado institucional. "
            "Ação imediata: revisar o formulário de registro do 1746 com categoria obrigatória. "
            "Métrica de sucesso: reduzir 'Outros' de 31% para menos de 5% em 6 meses."
        )
    st.markdown("---")

    # ── Insight B ────────────────────────────────────────────
    st.markdown('<p class="section-title">Insight B — Rock in Rio 2022: quase 1.000 reclamações em um único evento</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 3])
    with col_a:
        metric_card("Rock in Rio 1ª edição (3 dias)", "401 chamados")
        metric_card("Rock in Rio 2ª edição (4 dias)", "557 chamados")
        metric_card("Total combinado (7 dias)", "958 chamados")
        metric_card("Média diária combinada", "136,86/dia")

    with col_b:
        st.markdown(
            "O Rock in Rio 2022 teve duas edições no mesmo mês de setembro: a primeira de 02 a "
            "04/09 (3 dias) e a segunda de 08 a 11/09 (4 dias). Combinadas, geraram **958 chamados "
            "de perturbação do sossego em 7 dias**, a maior concentração de reclamações de barulho "
            "de qualquer evento do período."
        )
        analise(
            "O volume combinado de 958 chamados em 7 dias representa a maior concentração de "
            "reclamações de barulho de qualquer evento do período. Como o Rock in Rio é um evento "
            "recorrente, esse padrão pode ser antecipado e gerenciado. Recomenda-se criar um "
            "protocolo específico de gestão para o período do evento, incluindo reforço de equipes "
            "de fiscalização, canal de denúncias dedicado para moradores do entorno e monitoramento "
            "em tempo real dos chamados para acionar reforços de forma dinâmica."
        )
    st.markdown("---")

    # ── Insight C ────────────────────────────────────────────
    st.markdown('<p class="section-title">Insight C — Análise per capita inverte o ranking de bairros</p>',
                unsafe_allow_html=True)

    df_percapita = pd.DataFrame({
        "Bairro": ["Campo Grande", "Tijuca"],
        "Chamados": [125, 100],
        "Pop. estimada": ["~500.000 hab.", "~150.000 hab."],
        "1 chamado para cada": ["4.000 habitantes", "1.500 habitantes"],
        "Pressão proporcional": ["Baixa", "Alta"],
    })

    col_a, col_b = st.columns(2)
    with col_a:
        fig2 = px.bar(
            pd.DataFrame({
                "Bairro": ["Campo Grande\n(volume absoluto)", "Tijuca\n(volume absoluto)",
                           "Campo Grande\n(per capita)", "Tijuca\n(per capita)"],
                "Valor": [125, 100, 125/500, 100/150],
                "Métrica": ["Absoluto", "Absoluto", "Per capita", "Per capita"],
            }),
            x="Bairro", y="Valor", color="Métrica",
            color_discrete_map={"Absoluto": AZUL2, "Per capita": VERM},
            barmode="group",
            labels={"Valor": "Chamados (ou chamados/1.000 hab.)", "Bairro": ""},
            title="Volume Absoluto vs. Per Capita",
        )
        fig2.update_layout(height=340)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.dataframe(df_percapita, use_container_width=True, hide_index=True)
        st.markdown(
            "Campo Grande liderou em volume absoluto com 125 chamados. Tijuca ficou em 2º com 100. "
            "Mas Campo Grande tem ~500 mil habitantes e Tijuca ~150 mil. Proporcionalmente: "
            "Tijuca = 1 chamado por 1.500 hab.; Campo Grande = 1 chamado por 4.000 hab."
        )
        analise(
            "Analisar chamados por volume absoluto pode levar a alocação de recursos ineficiente. "
            "A análise per capita reverte a liderança: Tijuca apresenta maior pressão proporcional "
            "que Campo Grande. Recomendação: adotar chamados per capita como KPI primário para "
            "alocação de equipes por bairro, não volume absoluto."
        )
    st.markdown("---")

    # ── Insight D ────────────────────────────────────────────
    st.markdown('<p class="section-title">Insight D — O Rio de Janeiro nunca ficou "frio" em 2024</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig3 = px.line(
            DADOS_TEMP, x="mes", y="temp", markers=True, text="temp",
            color_discrete_sequence=[VERM],
            labels={"temp": "Temp. Média (°C)", "mes": "Mês"},
            title="Temperatura Média Mensal 2024 — nenhum mês abaixo de 20°C",
        )
        fig3.add_hline(y=20, line_dash="dash", line_color=AZUL2,
                       annotation_text="Limiar 'frio' carioca (20°C)")
        fig3.update_traces(texttemplate="%{text:.1f}°C", textposition="top center")
        fig3.update_layout(height=340, yaxis_range=[18, 29])
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown(
            "O mês mais frio de 2024 foi julho com **20,8°C**, exatamente no limite do critério "
            "de 'frio' (abaixo de 20°C). Em nenhum mês de 2024 o Rio atingiu esse limiar. "
            "Isso significa que o inimigo do lazer ao ar livre nos feriados cariocas em 2024 "
            "foi o **céu encoberto**, não a temperatura."
        )
        analise(
            "Os dados de 2024 mostram que nenhum mês ficou abaixo de 20°C de temperatura média. "
            "Isso tem consequência direta: nenhum feriado foi 'não aproveitável' por frio — "
            "todos os casos foram por condição climática desfavorável. Os dados não permitem "
            "afirmar se isso é representativo de outros anos."
        )


# ============================================================
# PÁGINA: RECOMENDAÇÕES
# ============================================================
elif pagina == "✅ Recomendações":
    st.title("✅ Recomendações Priorizadas")
    st.markdown(
        "Recomendações baseadas exclusivamente nos findings dos dados. "
        "Priorizadas por impacto e facilidade de implementação."
    )
    st.markdown("---")

    # Matriz de prioridade
    st.markdown('<p class="section-title">Matriz de Prioridade</p>', unsafe_allow_html=True)

    df_matriz = pd.DataFrame({
        "Recomendação": [
            "Corrigir qualidade dos dados de registro",
            "Protocolo preventivo para grandes eventos",
            "Análise per capita por bairro",
            "Investigar o fenômeno do Réveillon",
        ],
        "Impacto": ["Alto", "Alto", "Médio", "Médio"],
        "Esforço": ["Médio", "Baixo", "Baixo", "Médio"],
        "Prioridade": ["#1 — Imediata", "#2 — Imediata", "#3 — Curto prazo", "#4 — Estratégica"],
        "Prazo": ["3 a 6 meses", "Antes do próximo evento", "30 a 60 dias", "60 a 90 dias"],
    })
    st.dataframe(df_matriz, use_container_width=True, hide_index=True)
    st.markdown("---")

    rec_data = [
        {
            "titulo": "🔴 Prioridade 1 — IMEDIATA: Corrigir qualidade dos dados de registro",
            "problema": "31,6% dos chamados sem categoria e 12,6% sem localização comprometem toda a capacidade de análise e roteamento automático.",
            "acoes": [
                "Implementar campo de categoria obrigatório no formulário do 1746, sem opção em branco.",
                "Implementar validação de CEP ou logradouro obrigatório para chamados de serviços de campo.",
                "Criar lista padronizada com no máximo 20 categorias claras e mutuamente exclusivas.",
            ],
            "metrica": "Reduzir 'Outros' de 31% para menos de 5% e chamados sem localização de 12,6% para menos de 3%.",
            "prazo": "3 a 6 meses",
            "responsavel": "TI e Operações do 1746",
        },
        {
            "titulo": "🔴 Prioridade 2 — IMEDIATA: Protocolo preventivo para grandes eventos",
            "problema": "Rock in Rio gera +165,3% de reclamações de barulho de forma previsível e recorrente, sem evidência de preparação específica.",
            "acoes": [
                "Criar calendário anual de grandes eventos com datas de Rock in Rio, Carnaval e Réveillon.",
                "Definir protocolo de reforço das equipes de fiscalização de perturbação do sossego para períodos de evento.",
                "Monitorar chamados em tempo real durante eventos para acionar reforços de forma dinâmica.",
            ],
            "metrica": "Redução do pico de chamados durante Rock in Rio de +165% para menos de +100% em relação à média geral.",
            "prazo": "Antes do próximo evento de grande porte",
            "responsavel": "Fiscalização e Central 1746",
        },
        {
            "titulo": "🟡 Prioridade 3 — CURTO PRAZO: Análise per capita por bairro",
            "problema": "Alocação de recursos por bairro baseada em volume absoluto pode ser ineficiente, pois ignora diferenças populacionais.",
            "acoes": [
                "Cruzar dados de chamados com população por bairro (IBGE) para calcular taxa per capita.",
                "Adotar chamados por 10.000 habitantes como indicador primário de demanda por bairro.",
                "Revisar alocação de equipes de campo com base no novo indicador per capita.",
            ],
            "metrica": "Mapa de calor per capita disponível para apoio à tomada de decisão de alocação.",
            "prazo": "30 a 60 dias",
            "responsavel": "Análise de dados e Operações",
        },
        {
            "titulo": "🟡 Prioridade 4 — ESTRATÉGICA: Investigar o comportamento atípico do Réveillon",
            "problema": "O maior evento de rua do mundo gerou média diária abaixo do padrão habitual — fenômeno não explicado pelos dados disponíveis.",
            "acoes": [
                "Analisar o volume total de ligações recebidas pelo 1746 no período do Réveillon, não apenas as completadas.",
                "Mapear a distribuição geográfica dos chamados durante o Réveillon.",
                "Comparar com dados de outros anos de Réveillon para confirmar se o padrão se repete.",
            ],
            "metrica": "Hipótese sobre o fenômeno confirmada ou refutada com dados.",
            "prazo": "60 a 90 dias",
            "responsavel": "Análise de dados",
        },
    ]

    for rec in rec_data:
        with st.expander(rec["titulo"], expanded=True):
            st.markdown(f"**Problema:** {rec['problema']}")
            st.markdown("**Ações:**")
            for a in rec["acoes"]:
                st.markdown(f"  - {a}")
            cols = st.columns(3)
            with cols[0]:
                metric_card("Métrica de Sucesso", rec["metrica"])
            with cols[1]:
                metric_card("Prazo Sugerido", rec["prazo"])
            with cols[2]:
                metric_card("Responsável", rec["responsavel"])

    st.markdown("---")
    st.markdown("### Repositório e Acesso")
    st.markdown("""
- 🔗 **Código-fonte completo:** https://github.com/Bruno-Barradas/desafio-casa-civil
- 📊 **Dashboard interativo:** https://desafio-casa-civil-kehfquv8szpy26dgsxs7kl.streamlit.app
- 📄 Scripts SQL: `analise_sql.sql`
- 🐍 Scripts Python: `analise_python.py` / `analise_python.ipynb`
- 🌐 Scripts API: `analise_api.py` / `analise_api.ipynb`
    """)
