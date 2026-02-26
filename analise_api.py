# ============================================================
# DESAFIO TÉCNICO - ANALISTA DE DADOS
# analise_api.py
# Integração com APIs: Feriados (Nager.Date) + Clima (Open-Meteo)
# ============================================================

import requests
import pandas as pd
from datetime import date, datetime

# ============================================================
# CONFIGURAÇÕES
# ============================================================

YEAR = 2024
COUNTRY = "BR"

# Coordenadas do Rio de Janeiro
LAT = -22.9068
LON = -43.1729

# Data inicial e final para clima
START_DATE = "2024-01-01"
END_DATE = "2024-08-01"


# ============================================================
# HELPERS
# ============================================================

def get_holidays(year: int, country: str) -> pd.DataFrame:
    """Busca feriados na Public Holiday API."""
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country}"
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df["date"] = pd.to_datetime(df["date"])
    df["weekday"] = df["date"].dt.day_name()
    df["weekday_num"] = df["date"].dt.dayofweek  # 0=Monday, 6=Sunday
    return df


def get_weather(lat: float, lon: float, start: str, end: str) -> pd.DataFrame:
    """Busca dados climáticos históricos diários no Open-Meteo."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ["temperature_2m_mean", "weathercode"],
        "timezone": "America/Sao_Paulo",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()["daily"]
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df = df.rename(columns={
        "time": "date",
        "temperature_2m_mean": "temp_mean",
        "weathercode": "weather_code",
    })
    return df


# WMO weather code → descrição simplificada
# Referência: https://gist.github.com/stellasphere/9490c195ed2b53c707087c8c2db4ec0c
def wmo_description(code: int) -> str:
    if code == 0:
        return "Céu limpo"
    elif code in [1, 2]:
        return "Parcialmente nublado"
    elif code == 3:
        return "Totalmente nublado"
    elif code in [45, 48]:
        return "Nevoeiro"
    elif code in [51, 53, 55]:
        return "Garoa"
    elif code in [61, 63, 65]:
        return "Chuva"
    elif code in [71, 73, 75, 77]:
        return "Neve"
    elif code in [80, 81, 82]:
        return "Pancadas de chuva"
    elif code in [95, 96, 99]:
        return "Tempestade"
    else:
        return f"Código {code}"


def is_beach_weather(row) -> bool:
    """Retorna True se o dia é bom para ir à praia (sol e temp >= 20°C)."""
    cold = row["temp_mean"] < 20
    # Códigos ruins: totalmente nublado (3), chuva, tempestade, neve, nevoeiro
    bad_codes = {3, 45, 48, 51, 53, 55, 61, 63, 65, 71, 73, 75, 77, 80, 81, 82, 95, 96, 99}
    bad_weather = row["weather_code"] in bad_codes
    return not cold and not bad_weather


# ============================================================
# BUSCAR DADOS
# ============================================================

print("Buscando dados de feriados e clima...\n")
holidays_all = get_holidays(YEAR, COUNTRY)
weather = get_weather(LAT, LON, START_DATE, END_DATE)

# Feriados no período de clima (jan–ago)
holidays_period = holidays_all[
    holidays_all["date"] <= pd.Timestamp(END_DATE)
].copy()

# ============================================================
# PERGUNTA 1: Quantos feriados há no Brasil em 2024?
# ============================================================
print("=" * 60)
total_holidays = len(holidays_all)
print(f"1. Total de feriados nacionais no Brasil em 2024: {total_holidays}")
print(holidays_all[["date", "localName", "weekday"]].to_string(index=False))


# ============================================================
# PERGUNTA 2: Qual mês tem o maior número de feriados?
# ============================================================
print("\n" + "=" * 60)
holidays_all["month"] = holidays_all["date"].dt.month
by_month = (
    holidays_all.groupby("month")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)
by_month["month_name"] = by_month["month"].apply(
    lambda m: date(2024, m, 1).strftime("%B")
)
top_month = by_month.iloc[0]
print(f"2. Mês com mais feriados em 2024: {top_month['month_name']} ({top_month['count']} feriados)")
print(by_month[["month_name", "count"]].to_string(index=False))


# ============================================================
# PERGUNTA 3: Feriados em dias úteis (segunda a sexta)
# ============================================================
print("\n" + "=" * 60)
weekday_holidays = holidays_all[holidays_all["weekday_num"] < 5]
print(f"3. Feriados em 2024 que caem em dias úteis (seg–sex): {len(weekday_holidays)}")
print(weekday_holidays[["date", "localName", "weekday"]].to_string(index=False))


# ============================================================
# PERGUNTA 4: Temperatura média em cada mês (jan–ago 2024)
# ============================================================
print("\n" + "=" * 60)
weather["month"] = weather["date"].dt.month
monthly_temp = (
    weather.groupby("month")["temp_mean"]
    .mean()
    .round(2)
    .reset_index()
)
monthly_temp["month_name"] = monthly_temp["month"].apply(
    lambda m: date(2024, m, 1).strftime("%B")
)
print("4. Temperatura média mensal no Rio de Janeiro (jan–ago 2024):")
print(monthly_temp[["month_name", "temp_mean"]].to_string(index=False))


# ============================================================
# PERGUNTA 5: Tempo predominante em cada mês
# ============================================================
print("\n" + "=" * 60)

def predominant_weather(codes):
    """Retorna o weather_code mais frequente no período."""
    return codes.value_counts().idxmax()

monthly_weather = (
    weather.groupby("month")["weather_code"]
    .apply(predominant_weather)
    .reset_index()
)
monthly_weather["month_name"] = monthly_weather["month"].apply(
    lambda m: date(2024, m, 1).strftime("%B")
)
monthly_weather["descricao"] = monthly_weather["weather_code"].apply(wmo_description)
print("5. Tempo predominante por mês (jan–ago 2024):")
print(monthly_weather[["month_name", "weather_code", "descricao"]].to_string(index=False))


# ============================================================
# PERGUNTA 6: Tempo e temperatura média em cada feriado (jan–ago)
# ============================================================
print("\n" + "=" * 60)
holidays_weather = holidays_period.merge(
    weather[["date", "temp_mean", "weather_code"]],
    on="date",
    how="left",
)
holidays_weather["descricao_tempo"] = holidays_weather["weather_code"].apply(
    lambda c: wmo_description(c) if pd.notna(c) else "Sem dados"
)
print("6. Tempo e temperatura média em cada feriado (jan–ago 2024):")
print(
    holidays_weather[["date", "localName", "temp_mean", "weather_code", "descricao_tempo"]]
    .to_string(index=False)
)


# ============================================================
# PERGUNTA 7: Feriados "não aproveitáveis" em 2024
# ============================================================
print("\n" + "=" * 60)
# Apenas feriados com dados de clima disponíveis (jan–ago)
holidays_weather["aproveitavel"] = holidays_weather.apply(
    lambda row: is_beach_weather(row) if pd.notna(row["temp_mean"]) else None,
    axis=1
)

nao_aproveitaveis = holidays_weather[holidays_weather["aproveitavel"] == False]
print("7. Feriados NÃO aproveitáveis (frio < 20°C ou tempo ruim):")
if len(nao_aproveitaveis) > 0:
    print(
        nao_aproveitaveis[["date", "localName", "temp_mean", "descricao_tempo"]]
        .to_string(index=False)
    )
else:
    print("   Nenhum feriado não aproveitável encontrado no período.")

# Feriados fora do período de clima (ago–dez) não possuem dados
sem_dados = holidays_all[holidays_all["date"] > pd.Timestamp(END_DATE)]
if len(sem_dados) > 0:
    print(f"\n   Obs.: {len(sem_dados)} feriados após 01/08/2024 sem dados climáticos disponíveis:")
    print(sem_dados[["date", "localName"]].to_string(index=False))


# ============================================================
# PERGUNTA 8: Feriado "mais aproveitável" de 2024
# ============================================================
print("\n" + "=" * 60)
aproveitaveis = holidays_weather[holidays_weather["aproveitavel"] == True].copy()

if len(aproveitaveis) > 0:
    # Critério: menor weather_code (mais ensolarado) + maior temperatura
    # Normaliza ambos e combina em score
    aproveitaveis["score"] = (
        aproveitaveis["temp_mean"] - aproveitaveis["weather_code"] * 2
    )
    melhor = aproveitaveis.sort_values("score", ascending=False).iloc[0]
    print("8. Feriado mais aproveitável de 2024:")
    print(f"   Data     : {melhor['date'].date()}")
    print(f"   Feriado  : {melhor['localName']}")
    print(f"   Temp. média: {melhor['temp_mean']}°C")
    print(f"   Tempo    : {melhor['descricao_tempo']} (código {int(melhor['weather_code'])})")
else:
    print("8. Nenhum feriado aproveitável encontrado no período com dados.")

print("\nAnálise concluída!")
