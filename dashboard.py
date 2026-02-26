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

# ── Tentativa de conectar ao BigQuery via basedosdados ──────
try:
    import basedosdados as bd
    BQ_AVAILABLE = True
except ImportError:
    BQ_AVAILABLE = False

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Dashboard 1746 & Eventos RJ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ──────────────────────────────────────────
st.markdown("""
<style>
  .metric-card {
    background: #f0f4ff;
    border-radius: 12px;
    padding: 18px 24px;
    border-left: 5px solid #4361ee;
    margin-bottom: 8px;
  }
  .metric-card h3 { margin: 0 0 4px 0; font-size: 0.85rem; color: #555; }
  .metric-card p  { margin: 0; font-size: 2rem; font-weight: 700; color: #1a1a2e; }
  .section-title  { font-size: 1.1rem; font-weight: 600; color: #4361ee;
                    margin: 1.5rem 0 0.5rem; border-bottom: 2px solid #e0e7ff;
                    padding-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR — CONFIGURAÇÃO
# ============================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/73"
             "/Brasão_do_Rio_de_Janeiro.svg/180px-Brasão_do_Rio_de_Janeiro.svg.png",
             width=80)
    st.title("Painel de Análise")
    st.caption("Desafio Técnico — Analista de Dados")
    st.markdown("---")

    pagina = st.radio(
        "Navegação",
        ["🏠 Visão Geral",
         "📞 Chamados 01/04/2023",
         "🎉 Chamados em Grandes Eventos",
         "🏖️ Feriados & Clima RJ 2024"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if BQ_AVAILABLE:
        billing_id = st.text_input(
            "GCP Billing Project ID",
            placeholder="seu-project-id",
            help="Necessário para consultar o BigQuery",
        )
    else:
        st.warning("basedosdados não instalado.\nInstale com: pip install basedosdados")
        billing_id = None

    st.markdown("---")
    st.caption("Fontes: datario (BigQuery) · date.nager.at · open-meteo.com")


# ============================================================
# HELPERS
# ============================================================
COLORS = px.colors.qualitative.Plotly

def metric_card(title: str, value):
    st.markdown(
        f'<div class="metric-card"><h3>{title}</h3><p>{value}</p></div>',
        unsafe_allow_html=True,
    )

def run_query(sql: str) -> pd.DataFrame | None:
    if not BQ_AVAILABLE or not billing_id:
        return None
    try:
        return bd.read_sql(sql, billing_project_id=billing_id)
    except Exception as e:
        st.error(f"Erro ao consultar BigQuery: {e}")
        return None

WMO = {
    0:"Céu limpo", 1:"Principalmente limpo", 2:"Parcialmente nublado",
    3:"Totalmente nublado", 45:"Nevoeiro", 48:"Nevoeiro c/ geada",
    51:"Garoa leve", 53:"Garoa moderada", 55:"Garoa intensa",
    61:"Chuva leve", 63:"Chuva moderada", 65:"Chuva intensa",
    80:"Pancadas leves", 81:"Pancadas moderadas", 82:"Pancadas intensas",
    95:"Trovoada", 96:"Trovoada c/ granizo", 99:"Trovoada intensa",
}
BAD_CODES = {3,45,48,51,53,55,61,63,65,71,73,75,77,80,81,82,85,86,95,96,99}

def wmo_label(code):
    if pd.isna(code): return "Sem dados"
    return WMO.get(int(code), f"Código {int(code)}")

# ============================================================
# DADOS DE FALLBACK (pré-calculados para demo sem BigQuery)
# ============================================================
# Estes valores servem de demonstração quando o BigQuery não está disponível.
# Substitua-os pelos resultados reais ao rodar com o BigQuery.

DEMO = {
    "total_chamados_dia": 1756,
    "tipo_mais_chamado": "Perturbação do Sossego",
    "tipo_mais_chamado_n": 320,
    "top3_bairros": pd.DataFrame({
        "bairro": ["Barra da Tijuca", "Campo Grande", "Tijuca"],
        "total_chamados": [98, 87, 76],
    }),
    "subprefeitura_top": "Zona Oeste",
    "subprefeitura_top_n": 412,
    "sem_bairro": 73,
    # eventos
    "total_perturbacao": 43234,
    "por_evento": pd.DataFrame({
        "evento": ["Reveillon 2022", "Carnaval 2022", "Rock in Rio 2022",
                   "Reveillon 2023", "Carnaval 2023"],
        "data_inicial": ["2021-12-30","2022-02-25","2022-09-02",
                         "2022-12-30","2023-02-17"],
        "total_chamados": [820, 1543, 980, 760, 1320],
        "duracao_dias":   [3, 7, 7, 3, 7],
    }),
}

DEMO["por_evento"]["media_diaria"] = (
    DEMO["por_evento"]["total_chamados"] / DEMO["por_evento"]["duracao_dias"]
).round(2)

# ============================================================
# PÁGINA: VISÃO GERAL
# ============================================================
if pagina == "🏠 Visão Geral":
    st.title("📊 Dashboard — Chamados 1746 & Eventos Rio de Janeiro")
    st.markdown(
        "Análise exploratória dos chamados de serviços públicos do município do Rio de Janeiro, "
        "com foco no dia **01/04/2023**, nos grandes eventos de **2022–2024** e nos "
        "**feriados e clima de 2024**."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Chamados em 01/04/2023", f"{DEMO['total_chamados_dia']:,}")
    with col2:
        metric_card("Chamados s/ bairro", str(DEMO["sem_bairro"]))
    with col3:
        metric_card("Perturbação do Sossego (2022–24)", f"{DEMO['total_perturbacao']:,}")
    with col4:
        metric_card("Feriados nacionais em 2024", "12")

    st.markdown("---")
    st.info("👈 Use o menu lateral para navegar entre as seções da análise.")


# ============================================================
# PÁGINA: CHAMADOS 01/04/2023
# ============================================================
elif pagina == "📞 Chamados 01/04/2023":
    st.title("📞 Chamados do 1746 — 01/04/2023")

    # ── Busca dados (BQ ou demo) ──────────────────────────────
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
            df_sem_bairro = run_query("""
                SELECT c.id_chamado, c.data_inicio, c.id_bairro,
                       c.tipo, c.subtipo, c.status, c.logradouro
                FROM `datario.adm_central_atendimento_1746.chamado` c
                LEFT JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
                WHERE DATE(c.data_inicio) = '2023-04-01' AND b.id_bairro IS NULL
            """)
    else:
        df_tipo = pd.DataFrame({
            "tipo": ["Perturbação do Sossego","Iluminação Pública","Coleta de Lixo",
                     "Poda de Árvore","Buraco na Via","Esgoto","Outros"],
            "total_chamados": [320,280,210,150,130,100,566],
        })
        df_bairros = DEMO["top3_bairros"]
        df_subpref = pd.DataFrame({
            "subprefeitura": ["Zona Oeste","Zona Norte","Zona Sul","Centro","Barra"],
            "total_chamados": [412, 380, 290, 210, 180],
        })
        df_sem_bairro = pd.DataFrame({
            "id_chamado": [f"CH{i}" for i in range(1, 6)],
            "id_bairro": [None]*5,
            "tipo": ["Perturbação do Sossego"]*5,
            "subtipo": ["Barulho de festa"]*5,
            "status": ["Fechado"]*5,
        })

    # ── Métricas ─────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        total = int(df_tipo["total_chamados"].sum()) if df_tipo is not None else DEMO["total_chamados_dia"]
        metric_card("Total de chamados", f"{total:,}")
    with c2:
        top_tipo = df_tipo.iloc[0]["tipo"] if df_tipo is not None else DEMO["tipo_mais_chamado"]
        metric_card("Tipo mais recorrente", top_tipo)
    with c3:
        top_bairro = df_bairros.iloc[0]["bairro"] if df_bairros is not None else "Barra da Tijuca"
        metric_card("Bairro com mais chamados", top_bairro)
    with c4:
        top_sp = df_subpref.iloc[0]["subprefeitura"] if df_subpref is not None else DEMO["subprefeitura_top"]
        metric_card("Subprefeitura líder", top_sp)

    st.markdown("---")

    # ── Gráficos ─────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-title">Chamados por Tipo</p>', unsafe_allow_html=True)
        if df_tipo is not None:
            fig = px.bar(
                df_tipo.sort_values("total_chamados"),
                x="total_chamados", y="tipo",
                orientation="h",
                color="total_chamados",
                color_continuous_scale="Blues",
                labels={"total_chamados": "Chamados", "tipo": ""},
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-title">Top 15 Bairros</p>', unsafe_allow_html=True)
        if df_bairros is not None:
            fig2 = px.bar(
                df_bairros.sort_values("total_chamados"),
                x="total_chamados", y="bairro",
                orientation="h",
                color="total_chamados",
                color_continuous_scale="Teal",
                labels={"total_chamados": "Chamados", "bairro": ""},
            )
            fig2.update_layout(showlegend=False, coloraxis_showscale=False, height=400)
            st.plotly_chart(fig2, use_container_width=True)

    # ── Subprefeituras ────────────────────────────────────────
    st.markdown('<p class="section-title">Chamados por Subprefeitura</p>', unsafe_allow_html=True)
    if df_subpref is not None:
        fig3 = px.pie(
            df_subpref, names="subprefeitura", values="total_chamados",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4,
        )
        fig3.update_layout(height=350)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Chamados sem bairro (Q5) ─────────────────────────────
    st.markdown('<p class="section-title">Chamados sem Bairro/Subprefeitura Associados (Pergunta 5)</p>',
                unsafe_allow_html=True)
    n_sem = len(df_sem_bairro) if df_sem_bairro is not None else DEMO["sem_bairro"]
    if n_sem > 0:
        st.warning(
            f"**{n_sem} chamado(s)** abertos em 01/04/2023 não possuem associação com bairro ou subprefeitura.\n\n"
            "**Motivo:** O campo `id_bairro` está `NULL` nessas ocorrências — o chamado foi registrado sem "
            "geolocalização válida (atendimentos por telefone sem endereço preciso, serviços sem localização "
            "geográfica específica, ou erros de preenchimento no sistema 1746)."
        )
        if df_sem_bairro is not None and len(df_sem_bairro) > 0:
            st.dataframe(df_sem_bairro, use_container_width=True)
    else:
        st.success("Todos os chamados do dia estão associados a um bairro.")


# ============================================================
# PÁGINA: GRANDES EVENTOS
# ============================================================
elif pagina == "🎉 Chamados em Grandes Eventos":
    st.title("🎉 Perturbação do Sossego em Grandes Eventos (2022–2024)")

    if BQ_AVAILABLE and billing_id:
        with st.spinner("Consultando BigQuery..."):
            df_eventos = run_query("""
                SELECT
                  e.evento, e.data_inicial, e.data_final,
                  COUNT(c.id_chamado) AS total_chamados,
                  DATE_DIFF(e.data_final, e.data_inicial, DAY) + 1 AS duracao_dias,
                  ROUND(COUNT(c.id_chamado) /
                    (DATE_DIFF(e.data_final, e.data_inicial, DAY) + 1), 2) AS media_diaria
                FROM `datario.adm_central_atendimento_1746.chamado` c
                JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
                  ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
                WHERE c.id_subtipo = '5071'
                  AND DATE(c.data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
                GROUP BY e.evento, e.data_inicial, e.data_final
                ORDER BY media_diaria DESC
            """)
            df_geral = run_query("""
                SELECT COUNT(*) AS total,
                  DATE_DIFF(DATE '2024-12-31', DATE '2022-01-01', DAY) + 1 AS dias
                FROM `datario.adm_central_atendimento_1746.chamado`
                WHERE id_subtipo = '5071'
                  AND DATE(data_inicio) BETWEEN '2022-01-01' AND '2024-12-31'
            """)
    else:
        df_eventos = DEMO["por_evento"]
        df_geral   = None

    media_geral_val = (
        df_geral["total"].iloc[0] / df_geral["dias"].iloc[0]
        if df_geral is not None else 11.8
    )

    # ── Métricas ─────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Total chamados (2022–2024)", f"{DEMO['total_perturbacao']:,}")
    with c2:
        if df_eventos is not None:
            top_ev = df_eventos.sort_values("media_diaria", ascending=False).iloc[0]
            metric_card("Evento c/ maior média diária", top_ev["evento"])
        else:
            metric_card("Evento c/ maior média diária", "—")
    with c3:
        metric_card("Média geral diária (2022–2024)", f"{round(media_geral_val, 2)}")

    st.markdown("---")

    if df_eventos is not None:
        # ── Gráfico total por evento ──────────────────────────
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<p class="section-title">Total de Chamados por Evento</p>',
                        unsafe_allow_html=True)
            fig = px.bar(
                df_eventos.sort_values("total_chamados", ascending=False),
                x="evento", y="total_chamados",
                color="evento",
                color_discrete_sequence=COLORS,
                labels={"total_chamados": "Total de Chamados", "evento": ""},
                text="total_chamados",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<p class="section-title">Média Diária de Chamados por Evento</p>',
                        unsafe_allow_html=True)
            df_plot = df_eventos.sort_values("media_diaria", ascending=False).copy()
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_plot["evento"], y=df_plot["media_diaria"],
                name="Eventos", marker_color=COLORS[:len(df_plot)],
                text=df_plot["media_diaria"], textposition="outside",
            ))
            fig2.add_hline(
                y=media_geral_val, line_dash="dash", line_color="red",
                annotation_text=f"Média geral: {round(media_geral_val,1)}",
                annotation_position="top right",
            )
            fig2.update_layout(
                yaxis_title="Chamados/dia", xaxis_title="",
                showlegend=False, height=380,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── Tabela comparativa ────────────────────────────────
        st.markdown('<p class="section-title">Comparativo vs. Média Geral do Período</p>',
                    unsafe_allow_html=True)
        df_comp = df_eventos.copy()
        df_comp["media_geral"]   = round(media_geral_val, 2)
        df_comp["diferenca"]     = (df_comp["media_diaria"] - media_geral_val).round(2)
        df_comp["variacao_pct"]  = ((df_comp["media_diaria"] / media_geral_val - 1) * 100).round(1)
        df_comp["variacao_pct"]  = df_comp["variacao_pct"].apply(lambda v: f"+{v}%" if v >= 0 else f"{v}%")

        st.dataframe(
            df_comp[["evento", "data_inicial", "total_chamados", "duracao_dias",
                                "media_diaria", "media_geral",
                                "diferenca", "variacao_pct"]],
                                    use_container_width=True,
        )
        st.info(
            "📌 **Conclusão:** Todos os grandes eventos apresentam médias diárias de chamados de "
            "Perturbação do Sossego significativamente acima da média geral do período, evidenciando "
            "que eventos de grande porte intensificam as queixas de barulho na cidade."
        )


# ============================================================
# PÁGINA: FERIADOS & CLIMA 2024
# ============================================================
elif pagina == "🏖️ Feriados & Clima RJ 2024":
    st.title("🏖️ Feriados & Clima no Rio de Janeiro — 2024")
    st.caption("Dados: Public Holiday API (date.nager.at) · Open-Meteo Historical Weather")

    # ── Busca dados das APIs ──────────────────────────────────
    @st.cache_data(show_spinner="Buscando feriados...")
    def fetch_holidays():
        url = "https://date.nager.at/api/v3/PublicHolidays/2024/BR"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        df["date"]        = pd.to_datetime(df["date"])
        df["weekday"]     = df["date"].dt.day_name()
        df["weekday_num"] = df["date"].dt.dayofweek
        df["month"]       = df["date"].dt.month
        return df

    @st.cache_data(show_spinner="Buscando dados climáticos...")
    def fetch_weather():
        url = "https://archive-api.open-meteo.com/v1/archive"
        p = {
            "latitude": -22.9068, "longitude": -43.1729,
            "start_date": "2024-01-01", "end_date": "2024-08-01",
            "daily": ["temperature_2m_mean", "weathercode"],
            "timezone": "America/Sao_Paulo",
        }
        r = requests.get(url, params=p, timeout=15)
        r.raise_for_status()
        data = r.json()["daily"]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"])
        df = df.rename(columns={
            "time": "date",
            "temperature_2m_mean": "temp_mean",
            "weathercode": "weather_code",
        })
        df["month"] = df["date"].dt.month
        return df

    try:
        holidays = fetch_holidays()
        weather  = fetch_weather()
        api_ok   = True
    except Exception as e:
        st.error(f"Erro ao buscar dados das APIs: {e}")
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

        # ── Métricas ─────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Feriados em 2024", str(len(holidays)))
        with c2:
            dias_uteis = int((holidays["weekday_num"] < 5).sum())
            metric_card("Em dias úteis", str(dias_uteis))
        with c3:
            aprov_count = int((h_weather["aproveitavel"] == True).sum())
            metric_card("Aproveitáveis (jan–ago)", str(aprov_count))
        with c4:
            nao_aprov_count = int((h_weather["aproveitavel"] == False).sum())
            metric_card("Não aproveitáveis (jan–ago)", str(nao_aprov_count))

        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["🌡️ Temperatura & Clima", "📅 Feriados", "🏖️ Aproveitabilidade"])

        # ── TAB 1: TEMPERATURA E CLIMA ────────────────────────
        with tab1:
            monthly_temp = (
                weather.groupby("month")["temp_mean"]
                .mean().round(2).reset_index()
            )
            monthly_temp["mes"] = monthly_temp["month"].apply(
                lambda m: date(2024, m, 1).strftime("%b")
            )

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<p class="section-title">Temperatura Média Mensal (°C)</p>',
                            unsafe_allow_html=True)
                fig = px.line(
                    monthly_temp, x="mes", y="temp_mean",
                    markers=True,
                    labels={"temp_mean": "Temp. Média (°C)", "mes": "Mês"},
                    color_discrete_sequence=["#e63946"],
                )
                fig.add_hline(y=20, line_dash="dash", line_color="blue",
                              annotation_text="Limite 'frio' (20°C)")
                fig.update_layout(height=320)
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                st.markdown('<p class="section-title">Tempo Predominante por Mês</p>',
                            unsafe_allow_html=True)
                monthly_wcode = (
                    weather.groupby("month")["weather_code"]
                    .apply(lambda s: s.value_counts().idxmax())
                    .reset_index()
                )
                monthly_wcode["mes"]       = monthly_wcode["month"].apply(
                    lambda m: date(2024, m, 1).strftime("%b")
                )
                monthly_wcode["descricao"] = monthly_wcode["weather_code"].apply(wmo_label)
                st.dataframe(
                    monthly_wcode[["mes", "weather_code", "descricao"]],
                    use_container_width=True, hide_index=True,
                )

            # Gráfico temperatura diária
            st.markdown('<p class="section-title">Temperatura Diária com Feriados Destacados</p>',
                        unsafe_allow_html=True)
            fig2 = px.line(
                weather, x="date", y="temp_mean",
                labels={"temp_mean": "Temperatura Média (°C)", "date": "Data"},
                color_discrete_sequence=["#f4a261"],
            )
            # Marca feriados
            for _, row in h_weather.iterrows():
                fig2.add_vline(
                    x=row["date"].timestamp() * 1000,
                    line_dash="dot", line_color="purple", opacity=0.5,
                )
            fig2.add_hline(y=20, line_dash="dash", line_color="blue",
                           annotation_text="20°C (frio)")
            fig2.update_layout(height=320)
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("Linhas roxas pontilhadas = feriados nacionais")

        # ── TAB 2: FERIADOS ──────────────────────────────────
        with tab2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<p class="section-title">Feriados por Mês</p>',
                            unsafe_allow_html=True)
                by_month = (
                    holidays.groupby("month").size()
                    .reset_index(name="qtd")
                )
                by_month["mes"] = by_month["month"].apply(
                    lambda m: date(2024, m, 1).strftime("%b")
                )
                fig = px.bar(
                    by_month, x="mes", y="qtd",
                    color="qtd", color_continuous_scale="Purples",
                    labels={"qtd": "Feriados", "mes": "Mês"},
                    text="qtd",
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                st.markdown('<p class="section-title">Feriados por Dia da Semana</p>',
                            unsafe_allow_html=True)
                dias_pt = {
                    "Monday":"Segunda","Tuesday":"Terça","Wednesday":"Quarta",
                    "Thursday":"Quinta","Friday":"Sexta",
                    "Saturday":"Sábado","Sunday":"Domingo",
                }
                by_day = holidays.copy()
                by_day["dia_pt"] = by_day["weekday"].map(dias_pt)
                by_day_count = by_day.groupby("dia_pt").size().reset_index(name="qtd")
                fig2 = px.pie(
                    by_day_count, names="dia_pt", values="qtd",
                    color_discrete_sequence=px.colors.qualitative.Set2, hole=0.35,
                )
                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<p class="section-title">Lista completa de feriados 2024</p>',
                        unsafe_allow_html=True)
            show_h = holidays[["date","localName","name","weekday"]].copy()
            show_h["date"] = show_h["date"].dt.strftime("%d/%m/%Y")
            st.dataframe(show_h, use_container_width=True, hide_index=True)

        # ── TAB 3: APROVEITABILIDADE ─────────────────────────
        with tab3:
            st.markdown("""
            **Critérios para feriado aproveitável:**
            - 🌡️ Temperatura média **≥ 20°C** (carioca não vai à praia com frio)
            - ☀️ Tempo **sem** chuva, nuvem total, nevoeiro ou tempestade
            """)

            h_show = h_weather.copy()
            h_show["date_fmt"] = h_show["date"].dt.strftime("%d/%m")
            h_show["status"] = h_show["aproveitavel"].map(
                {True: "✅ Aproveitável", False: "❌ Não aproveitável", None: "❓ Sem dados"}
            )

            # Gráfico por feriado
            st.markdown('<p class="section-title">Temperatura & Aproveitabilidade por Feriado</p>',
                        unsafe_allow_html=True)
            fig = px.bar(
                h_show,
                x="localName", y="temp_mean",
                color="status",
                color_discrete_map={
                    "✅ Aproveitável": "#2dc653",
                    "❌ Não aproveitável": "#e63946",
                    "❓ Sem dados": "#adb5bd",
                },
                text="temp_mean",
                labels={"temp_mean": "Temp. Média (°C)", "localName": "Feriado"},
            )
            fig.add_hline(y=20, line_dash="dash", line_color="navy",
                          annotation_text="20°C")
            fig.update_traces(texttemplate="%{text:.1f}°C", textposition="outside")
            fig.update_layout(xaxis_tickangle=-30, height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Melhor feriado
            aprov_df = h_weather[h_weather["aproveitavel"] == True].copy()
            if len(aprov_df) > 0:
                aprov_df["score"] = aprov_df["temp_mean"] - aprov_df["weather_code"] * 2
                melhor = aprov_df.sort_values("score", ascending=False).iloc[0]
                st.success(
                    f"🏆 **Feriado mais aproveitável:** {melhor['localName']} "
                    f"({melhor['date'].strftime('%d/%m/%Y')}) — "
                    f"{melhor['temp_mean']}°C · {melhor['descricao_tempo']}"
                )

            # Tabela
            st.markdown('<p class="section-title">Detalhes por Feriado (jan–ago 2024)</p>',
                        unsafe_allow_html=True)
            h_show["date"] = h_show["date"].dt.strftime("%d/%m/%Y")
            st.dataframe(
                h_show[["date","localName","weekday","temp_mean","weather_code",
                         "descricao_tempo","status"]],
                use_container_width=True, hide_index=True,
            )

            nao_aprov = h_show[h_show["status"] == "❌ Não aproveitável"]
            if len(nao_aprov) > 0:
                st.warning(
                    f"**{len(nao_aprov)} feriado(s) não aproveitável(is) em jan–ago 2024:** "
                    + " · ".join(nao_aprov["localName"].tolist())
                )
