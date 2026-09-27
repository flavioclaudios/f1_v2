import streamlit as st
import pandas as pd
import requests
import urllib3
import plotly.express as px
from datetime import datetime
import pytz

# Desativa alertas de certificados SSL não verificados para a API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────
st.set_page_config(
    page_title="F1 2026 · Season Hub",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── DICIONÁRIOS E CONSTANTES GLOBAIS ───────────────────────────────
COUNTRY_FLAGS = {
    "Bahrain": "bh", "Saudi Arabia": "sa", "Australia": "au", "China": "cn",
    "USA": "us", "Italy": "it", "Monaco": "mc", "Spain": "es", "Canada": "ca",
    "Austria": "at", "UK": "gb", "Hungary": "hu", "Belgium": "be",
    "Netherlands": "nl", "Azerbaijan": "az", "Singapore": "sg",
    "Mexico": "mx", "Brazil": "br", "Qatar": "qa", "UAE": "ae", "Japan": "jp"
}

TEAM_COLORS = {
    "Mercedes":        "#00D2BE", "Ferrari":         "#E8002D",
    "Red Bull":        "#3671C6", "McLaren":         "#FF8000",
    "Aston Martin":    "#358C75", "Alpine F1 Team":  "#FF87BC",
    "Williams":        "#64C4FF", "RB F1 Team":      "#6692FF",
    "Kick Sauber":     "#52E252", "Haas F1 Team":    "#B6BABD",
    "Audi":            "#C0121B", "Cadillac F1 Team": "#CC0000",
}

FLAG_URLS = {
    "British": "gb", "Dutch": "nl", "Italian": "it", "Spanish": "es",
    "French": "fr", "Finnish": "fi", "Australian": "au", "German": "de",
    "Canadian": "ca", "Japanese": "jp", "Monegasque": "mc", "Chinese": "cn",
    "Danish": "dk", "New Zealander": "nz", "Thai": "th", "Brazilian": "br",
    "Argentine": "ar", "Austrian": "at", "Mexican": "mx",
}

TZ_MAP = {
    "Bahrain": "Asia/Bahrain", "Saudi Arabia": "Asia/Riyadh", "Australia": "Australia/Melbourne",
    "China": "Asia/Shanghai", "Japan": "Asia/Tokyo", "USA": "America/New_York",
    "Italy": "Europe/Rome", "Monaco": "Europe/Monaco", "Spain": "Europe/Madrid",
    "Canada": "America/Toronto", "Austria": "Europe/Vienna", "UK": "Europe/London",
    "Hungary": "Europe/Budapest", "Belgium": "Europe/Brussels", "Netherlands": "Europe/Amsterdam",
    "Azerbaijan": "Asia/Baku", "Singapore": "Asia/Singapore", "Mexico": "America/Mexico_City",
    "Brazil": "America/Sao_Paulo", "Qatar": "Asia/Qatar", "UAE": "Asia/Dubai"
}

# ── DADOS FIXOS PARA GARANTIR O FUNCIONAMENTO (FALLBACK) ─────────────────────
FALLBACK_RACES = [
    {'raceName': 'Bahrain Grand Prix', 'date': '2026-03-01', 'time': '15:00:00Z', 'Circuit': {'circuitName': 'Bahrain International Circuit', 'Location': {'locality': 'Sakhir', 'country': 'Bahrain', 'lat': '26.0325', 'long': '50.5106'}}, 'laps': 57, 'circuitLengthKm': 5.412, 'raceDistanceKm': 308.238, 'lapRecord': {'time': '1:31.447', 'driver': 'Pedro de la Rosa', 'year': 2005}, 'lastWinner': {'driver': 'Max Verstappen', 'team': 'Red Bull', 'year': 2025}, 'sessions': {'Practice 1': '2026-02-27T11:30:00Z', 'Practice 2': '2026-02-27T15:00:00Z', 'Qualifying': '2026-02-28T15:00:00Z', 'Race': '2026-03-01T15:00:00Z'}, 'weatherForecast': 'TBA'},
    {'raceName': 'Saudi Arabian Grand Prix', 'date': '2026-03-15', 'time': '17:00:00Z', 'Circuit': {'circuitName': 'Jeddah Corniche Circuit', 'Location': {'locality': 'Jeddah', 'country': 'Saudi Arabia', 'lat': '21.6319', 'long': '39.1044'}}, 'laps': 50, 'circuitLengthKm': 6.174, 'raceDistanceKm': 308.45, 'lapRecord': {'time': '1:30.734', 'driver': 'Lewis Hamilton', 'year': 2021}, 'lastWinner': {'driver': 'Max Verstappen', 'team': 'Red Bull', 'year': 2025}, 'sessions': {'Practice 1': '2026-03-13T13:30:00Z', 'Practice 2': '2026-03-13T17:00:00Z', 'Qualifying': '2026-03-14T17:00:00Z', 'Race': '2026-03-15T17:00:00Z'}, 'weatherForecast': 'TBA'},
    {'raceName': 'Australian Grand Prix', 'date': '2026-03-29', 'time': '04:00:00Z', 'Circuit': {'circuitName': 'Albert Park Circuit', 'Location': {'locality': 'Melbourne', 'country': 'Australia', 'lat': '-37.8497', 'long': '144.968'}}, 'laps': 58, 'circuitLengthKm': 5.278, 'raceDistanceKm': 306.124, 'lapRecord': {'time': '1:19.813', 'driver': 'Sergio Perez', 'year': 2023}, 'lastWinner': {'driver': 'Carlos Sainz', 'team': 'Ferrari', 'year': 2024}, 'sessions': {'Practice 1': '2026-03-27T01:30:00Z', 'Practice 2': '2026-03-27T05:00:00Z', 'Qualifying': '2026-03-28T05:00:00Z', 'Race': '2026-03-29T04:00:00Z'}, 'weatherForecast': 'TBA'},
    {'raceName': 'Japanese Grand Prix', 'date': '2026-04-12', 'time': '05:00:00Z', 'Circuit': {'circuitName': 'Suzuka International Racing Course', 'Location': {'locality': 'Suzuka', 'country': 'Japan', 'lat': '34.8431', 'long': '136.541'}}, 'laps': 53, 'circuitLengthKm': 5.807, 'raceDistanceKm': 307.471, 'lapRecord': {'time': '1:30.983', 'driver': 'Lewis Hamilton', 'year': 2019}, 'lastWinner': {'driver': 'Max Verstappen', 'team': 'Red Bull', 'year': 2025}, 'sessions': {'Practice 1': '2026-04-10T02:30:00Z', 'Practice 2': '2026-04-10T06:00:00Z', 'Qualifying': '2026-04-11T06:00:00Z', 'Race': '2026-04-12T05:00:00Z'}, 'weatherForecast': 'TBA'},
    {'raceName': 'Brazilian Grand Prix', 'date': '2026-11-08', 'time': '17:00:00Z', 'Circuit': {'circuitName': 'Autodromo Jose Carlos Pace', 'Location': {'locality': 'Sao Paulo', 'country': 'Brazil', 'lat': '-23.7036', 'long': '-46.6997'}}, 'laps': 71, 'circuitLengthKm': 4.309, 'raceDistanceKm': 305.879, 'lapRecord': {'time': '1:10.540', 'driver': 'Valtteri Bottas', 'year': 2018}, 'lastWinner': {'driver': 'Max Verstappen', 'team': 'Red Bull', 'year': 2024}, 'sessions': {'Practice 1': '2026-11-06T14:30:00Z', 'Practice 2': '2026-11-06T18:00:00Z', 'Qualifying': '2026-11-07T17:00:00Z', 'Race': '2026-11-08T17:00:00Z'}, 'weatherForecast': 'TBA'},
]

# ── FUNÇÕES E UTILITÁRIOS ───────────────────────────────
@st.cache_data(ttl=3600)
def fetch_data(endpoint):
    """Busca dados da API com fallback para erros."""
    url = f"https://api.jolpi.ca/ergast/f1/2026/{endpoint}.json"
    try:
        r = requests.get(url, verify=False, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.sidebar.warning(f"Erro ao buscar '{endpoint}': Usando cache/fallback.")
        return None

def flag_url(nat): 
    code = FLAG_URLS.get(nat)
    return f"https://flagcdn.com/w40/{code}.png" if code else ""

def team_color(team): 
    return TEAM_COLORS.get(team, "#3A3A5A")

def safe_html(text): 
    return str(text).replace('"', "&quot;").replace("'", "&#39;").replace("<", "&lt;").replace(">", "&gt;")

# ── ESTILOS CSS ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #07070F; color: #E8E8E8; }
.stApp, [data-testid="stAppViewContainer"] { background: #07070F; }
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #0D0D1A; }
#MainMenu, footer, header { visibility: hidden; }

.block-container { padding-top: 0 !important; max-width: 100% !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; }

/* Hero Section */
.hero-wrap { background: linear-gradient(135deg, #0D0010 0%, #07070F 55%, #100005 100%); border-bottom: 2px solid #E10600; padding: 2.5rem 2rem 2rem; margin-bottom: 2rem; position: relative; overflow: hidden; }
.hero-wrap::before { content: "F1"; position: absolute; right: -1rem; top: -1.5rem; font-family: 'Rajdhani', sans-serif; font-size: 8rem; font-weight: 700; color: rgba(225,6,0,0.04); line-height: 1; pointer-events: none; }
.hero-title { font-family: 'Rajdhani', sans-serif; font-size: 3rem; font-weight: 700; letter-spacing: 0.04em; color: #FFF; line-height: 1; margin: 0; }
.hero-title .year { color: #E10600; }
.hero-sub { font-size: 0.75rem; font-weight: 500; letter-spacing: 0.2em; text-transform: uppercase; color: #666; margin: 0 0 0.4rem 0; }

/* Titles */
.section-label { font-family: 'Rajdhani', sans-serif; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; color: #E10600; margin-bottom: 0.25rem; }
.section-title { font-family: 'Rajdhani', sans-serif; font-size: 1.65rem; font-weight: 700; color: #FFF; margin: 0 0 1rem 0; letter-spacing: 0.02em; }

/* Driver Cards */
.driver-card { background: #0F0F1C; border: 1px solid #1C1C2E; border-radius: 8px; display: flex; align-items: center; margin-bottom: 0.45rem; transition: border-color 0.2s, transform 0.15s; min-height: 68px; flex-wrap: wrap; }
.driver-card:hover { border-color: #30304A; transform: translateX(4px); }
.card-accent { width: 4px; min-width: 4px; align-self: stretch; min-height: 68px; border-radius: 8px 0 0 8px; flex-shrink: 0; }
.card-pos { font-family: 'Rajdhani', sans-serif; font-size: 1.5rem; font-weight: 700; color: rgba(255,255,255,0.13); width: 3rem; min-width: 3rem; text-align: center; flex-shrink: 0; }
.card-pos.top3 { color: rgba(255,255,255,0.45); }
.card-info { flex: 1; padding: 0 0.8rem; min-width: 0; }
.card-name { font-family: 'Rajdhani', sans-serif; font-size: 1rem; font-weight: 600; color: #FFF; letter-spacing: 0.03em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.2; }
.card-meta { display: flex; align-items: center; gap: 0.45rem; margin-top: 0.2rem; }
.card-flag { height: 12px; border-radius: 1px; flex-shrink: 0; display: block; }
.card-team { font-size: 0.7rem; color: #777; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-pts { font-family: 'Rajdhani', sans-serif; font-size: 1.5rem; font-weight: 700; color: #FFF; padding: 0 1.1rem; flex-shrink: 0; line-height: 1.1; text-align: right; }
.card-pts-label { display: block; font-size: 0.58rem; font-weight: 400; color: #444; text-transform: uppercase; letter-spacing: 0.12em; text-align: right; }

/* Constructor Rows */
.ctor-row { background: #0F0F1C; border: 1px solid #1C1C2E; border-radius: 8px; display: flex; align-items: center; margin-bottom: 0.4rem; transition: border-color 0.2s; min-height: 56px; }
.ctor-row:hover { border-color: #30304A; }
.ctor-pos { font-family: 'Rajdhani', sans-serif; font-size: 1.25rem; font-weight: 700; color: rgba(255,255,255,0.15); width: 2.8rem; min-width: 2.8rem; text-align: center; flex-shrink: 0; }
.ctor-name { font-family: 'Rajdhani', sans-serif; font-size: 0.9rem; font-weight: 600; color: #FFF; letter-spacing: 0.03em; flex: 1; padding: 0 0.8rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ctor-pts { font-family: 'Rajdhani', sans-serif; font-size: 1.25rem; font-weight: 700; color: #FFF; padding: 0 1rem; flex-shrink: 0; line-height: 1.1; text-align: right; }
.ctor-pts small { display: block; font-size: 0.55rem; font-weight: 400; color: #444; text-transform: uppercase; letter-spacing: 0.1em; }

/* Diver & Next Race */
.f1-divider { border: none; border-top: 1px solid #181826; margin: 2rem 0; }
.next-race-card { background: #0F0F1C; border: 1px solid #1C1C2E; border-radius: 8px; padding: 1.5rem; color: #FFFFFF; font-size: 0.95rem; display: flex; flex-direction: column; gap: 0.4rem; }
.next-race-title { font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; font-weight: 700; color: #FFF; margin-bottom: 0.2rem;}
.next-race-sub { color: #E10600; font-weight: 700; letter-spacing: 0.1em; font-size: 0.85rem; margin-bottom: 0.5rem; text-transform: uppercase;}
.race-details { background: #131322; border: 1px solid #1C1C2E; border-radius: 8px; padding: 1rem; margin-top: 1rem; color: #CCCCCC;}
.race-details summary { font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; font-weight: 600; color: #00D2BE; cursor: pointer; outline: none; }
.race-details summary:hover { color: #00E676; }
.race-details ul { padding-left: 1.5rem; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-wrap">'
    '<p class="hero-sub">FIA Formula One World Championship</p>'
    '<h1 class="hero-title">Season <span class="year">2026</span> Hub</h1>'
    '</div>',
    unsafe_allow_html=True
)

# ── CLASSIFICAÇÃO (STANDINGS) ──────────────────────────────────────────────────
col_drivers, col_ctors = st.columns([3, 2], gap="large")

with col_drivers:
    st.markdown('<div class="section-label">Championship</div><div class="section-title">Driver Standings</div>', unsafe_allow_html=True)
    data_drivers = fetch_data("driverStandings")
    
    try:
        standings = data_drivers["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
    except (TypeError, KeyError, IndexError):
        standings = []
        st.info("Aguardando início da temporada para dados de pilotos.")

    for d in standings:
        pos = int(d.get("position", 0))
        fname = d["Driver"].get("familyName", "")
        gname = d["Driver"].get("givenName", "")
        nat = d["Driver"].get("nationality", "")
        
        team_data = d.get("Constructors", [{}])[0]
        team = team_data.get("name", "Unknown")
        pts = d.get("points", "0")
        color = team_color(team)
        
        flag = flag_url(nat)
        flag_block = f'<img class="card-flag" src="{flag}" alt="{safe_html(nat)}">' if flag else ""
        
        st.markdown(f'''
            <div class="driver-card">
                <div class="card-accent" style="background:{color};"></div>
                <div class="card-pos {'top3' if pos<=3 else ''}">{pos}</div>
                <div class="card-info">
                    <div class="card-name">{safe_html(gname + " " + fname)}</div>
                    <div class="card-meta">{flag_block}<span class="card-team">{safe_html(team)}</span></div>
                </div>
                <div class="card-pts">{pts}<span class="card-pts-label">PTS</span></div>
            </div>
        ''', unsafe_allow_html=True)

with col_ctors:
    st.markdown('<div class="section-label">Championship</div><div class="section-title">Constructor Standings</div>', unsafe_allow_html=True)
    data_const = fetch_data("constructorStandings")
    
    try:
        ctor_standings = data_const["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
    except (TypeError, KeyError, IndexError):
        ctor_standings = []
        st.info("Aguardando início da temporada para construtores.")

    for c in ctor_standings:
        pos = int(c.get("position", 0))
        name = c["Constructor"].get("name", "")
        pts = c.get("points", "0")
        color = team_color(name)
        
        st.markdown(f'''
            <div class="ctor-row">
                <div class="card-accent" style="background:{color}; min-height:56px; border-radius:8px 0 0 8px;"></div>
                <div class="ctor-pos">{pos}</div>
                <div class="ctor-name">{safe_html(name)}</div>
                <div class="ctor-pts">{pts}<small>PTS</small></div>
            </div>
        ''', unsafe_allow_html=True)


# ── LÓGICA DE CALENDÁRIO E PRÓXIMA CORRIDA ───────────────────────────────────
st.markdown('<hr class="f1-divider">', unsafe_allow_html=True)

data_cal = fetch_data("schedule")
try:
    races = data_cal['MRData']['RaceTable']['Races']
except (TypeError, KeyError):
    races = FALLBACK_RACES

fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_br)

proximo_race = None

# Identificar a próxima corrida
for r in races:
    try:
        race_time = r.get('time', '00:00:00Z').replace('Z', '')
        dt_utc = pd.to_datetime(f"{r['date']} {race_time}", utc=True)
        data_br = dt_utc.tz_convert(fuso_br)
        
        if data_br > agora:
            proximo_race = r
            break
    except Exception:
        continue

# Renderizar layout do Mapa e Next Race Lado a Lado
col_map, col_next = st.columns([2, 1], gap="medium")

with col_next:
    st.markdown('<div class="section-label">On Track</div><div class="section-title">Next Event</div>', unsafe_allow_html=True)
    
    if proximo_race:
        try:
            circuito = proximo_race['Circuit'].get('circuitName', "TBA")
            loc = proximo_race['Circuit'].get('Location', {})
            country = loc.get('country', "TBA")
            local = f"{loc.get('locality','TBA')}, {country}"

            # Horários
            race_time_str = proximo_race.get('time', '00:00:00Z').replace('Z', '')
            dt_utc = pd.to_datetime(f"{proximo_race['date']} {race_time_str}", utc=True)
            hora_sp = dt_utc.tz_convert(fuso_br).strftime('%d/%m %H:%M')

            tz_local = TZ_MAP.get(country)
            hora_local = dt_utc.tz_convert(tz_local).strftime('%d/%m %H:%M') if tz_local else "TBA"

            # Bandeira
            flag_code = COUNTRY_FLAGS.get(country)
            flag_img = f'<img class="card-flag" style="display:inline; height:14px;" src="https://flagcdn.com/w40/{flag_code}.png">' if flag_code else ""

            # Dados Extras Fallback
            laps = proximo_race.get('laps', 'TBA')
            dist = proximo_race.get('raceDistanceKm', 'TBA')
            rec_time = proximo_race.get('lapRecord', {}).get('time', 'TBA')
            rec_driver = proximo_race.get('lapRecord', {}).get('driver', 'TBA')

            # Render HTML
            st.markdown(f"""
                <div class="next-race-card">
                    <div class="next-race-sub">NEXT GRAND PRIX</div>
                    <div class="next-race-title">{proximo_race['raceName']}</div>
                    <div>📍 {circuito}</div>
                    <div>{flag_img} {local}</div>
                    <hr style="border-color: #1C1C2E; margin: 0.5rem 0;">
                    <div>🕒 Local: <strong>{hora_local}</strong></div>
                    <div>🕒 Brasília: <strong style="color:#00D2BE;">{hora_sp} BRT</strong></div>
                </div>

                <details class="race-details">
                  <summary>Detalhes do Circuito</summary>
                  <div>🏎️ <strong>Voltas:</strong> {laps}</div>
                  <div>📏 <strong>Distância:</strong> {dist} km</div>
                  <div>⏱️ <strong>Recorde:</strong> {rec_time} ({rec_driver})</div>
                </details>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error("Erro ao processar dados da próxima corrida.")
    else:
        st.info("Temporada encerrada ou dados indisponíveis.")

with col_map:
    st.markdown('<div class="section-label">Calendar</div><div class="section-title">World Circuit · F1 2026</div>', unsafe_allow_html=True)
    
    map_data = []
    
    for r in races:
        try:
            race_time = r.get('time', '00:00:00Z').replace('Z', '')
            dt_utc = pd.to_datetime(f"{r['date']} {race_time}", utc=True)
            horario_brasilia = dt_utc.tz_convert(fuso_br)
            data_formatada = horario_brasilia.strftime('%d/%m/%Y %H:%M')
            
            is_next = proximo_race and r['raceName'] == proximo_race['raceName']
            
            if is_next:
                status = "PRÓXIMO GP"
            elif horario_brasilia < agora:
                status = "Corrida Realizada"
            else:
                status = "Futura"
                
            location = r['Circuit']['Location']
            
            map_data.append({
                "Etapa": f"R{r.get('round', '?')}",
                "Grande Prêmio": r['raceName'],
                "Circuito": r['Circuit']['circuitName'],
                "Local": f"{location.get('locality')}, {location.get('country')}",
                "Data/Hora (BR)": data_formatada,
                "lat": float(location.get('lat', 0)),
                "lon": float(location.get('long', 0)),
                "Status": status
            })
        except Exception:
            continue
            
    if map_data:
        df_map = pd.DataFrame(map_data)
        df_map = df_map[(df_map['lat'] != 0) & (df_map['lon'] != 0)]
        df_map["Tamanho_Marcador"] = df_map['Status'].map({"Corrida Realizada": 8, "PRÓXIMO GP": 18, "Futura": 8})
        
        # Corrigido aviso DeprecationWarning do Plotly (uso do scatter_map em vez de scatter_mapbox)
        fig = px.scatter_map(
            df_map, lat="lat", lon="lon", color="Status",
            color_discrete_map={"Corrida Realizada": "#757575", "PRÓXIMO GP": "#00E676", "Futura": "#FF4B4B"},
            size="Tamanho_Marcador", size_max=18, hover_name="Grande Prêmio",
            hover_data={"Etapa": True, "Circuito": True, "Local": True, "Data/Hora (BR)": True, "Status": True, "Tamanho_Marcador": False, "lat": False, "lon": False},
            zoom=1, height=450
        )
        
        fig.update_layout(
            map_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor="#07070F", plot_bgcolor="#07070F",
            legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.02, font=dict(color="#FAFAFA"), bgcolor="rgba(7, 7, 15, 0.7)")
        )
        
        # Corrigido aviso DeprecationWarning do Streamlit (uso do width="stretch")
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Dados do mapa indisponíveis no momento.")
