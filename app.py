import streamlit as st
import pandas as pd
import requests
import urllib3
import plotly.express as px
from datetime import datetime
import pytz

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dicionário de países para bandeiras (mantido como fallback e para o mapa)
COUNTRY_FLAGS = {
    "Bahrain": "bh", "Saudi Arabia": "sa", "Australia": "au", "China": "cn", 
    "USA": "us", "Italy": "it", "Monaco": "mc", "Spain": "es", "Canada": "ca", 
    "Austria": "at", "UK": "gb", "Hungary": "hu", "Belgium": "be", 
    "Netherlands": "nl", "Azerbaijan": "az", "Singapore": "sg", 
    "Mexico": "mx", "Brazil": "br", "Qatar": "qa", "UAE": "ae", "Japan": "jp"
}

st.set_page_config(
    page_title="F1 2026 · Season Hub",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def get_next_race(data_cal):
    if not data_cal or 'RaceTable' not in data_cal['MRData']:
        return None
    
    races = data_cal['MRData']['RaceTable']['Races']
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_br)
    
    for r in races:
        # Cria o objeto datetime
        dt = pd.to_datetime(f"{r['date']} {r.get('time', '00:00:00Z').replace('Z', '')}")
        data_br = dt.tz_localize('UTC').tz_convert('America/Sao_Paulo')
        
        if data_br > agora:
            return {
                "nome": r['raceName'], 
                "data": data_br.strftime('%d/%m às %H:%M'), 
                "circuito": r['Circuit']['circuitName']
            }
    return None

# ── LISTA MESTRE (DEFINA ISTO LOGO APÓS OS IMPORTS E FUNÇÕES) ──────────────
FULL_CALENDAR = {
    "Bahrain Grand Prix": {"lat": 26.0325, "lon": 50.5106},
    "Saudi Arabian Grand Prix": {"lat": 21.6319, "lon": 39.1044},
    "Australian Grand Prix": {"lat": -37.8497, "lon": 144.968},
    "Chinese Grand Prix": {"lat": 31.3389, "lon": 121.220},
    "Miami Grand Prix": {"lat": 25.958, "lon": -80.2389},
    "Emilia Romagna Grand Prix": {"lat": 44.3439, "lon": 11.7167},
    "Monaco Grand Prix": {"lat": 43.7347, "lon": 7.4206},
    "Spanish Grand Prix": {"lat": 41.5700, "lon": 2.2611},
    "Canadian Grand Prix": {"lat": 45.5000, "lon": -73.5228},
    "Austrian Grand Prix": {"lat": 47.2197, "lon": 14.7647},
    "British Grand Prix": {"lat": 52.0786, "lon": -1.0169},
    "Hungarian Grand Prix": {"lat": 47.5789, "lon": 19.2486},
    "Belgian Grand Prix": {"lat": 50.4372, "lon": 5.9714},
    "Dutch Grand Prix": {"lat": 52.3888, "lon": 4.5409},
    "Italian Grand Prix": {"lat": 45.6156, "lon": 9.2819},
    "Azerbaijan Grand Prix": {"lat": 40.3725, "lon": 49.8533},
    "Singapore Grand Prix": {"lat": 1.2914, "lon": 103.864},
    "United States Grand Prix": {"lat": 30.1328, "lon": -97.6411},
    "Mexico City Grand Prix": {"lat": 19.4042, "lon": -99.0908},
    "São Paulo Grand Prix": {"lat": -23.7036, "lon": -46.6997},
    "Las Vegas Grand Prix": {"lat": 36.1147, "lon": -115.173},
    "Qatar Grand Prix": {"lat": 25.49, "lon": 51.454},
    "Abu Dhabi Grand Prix": {"lat": 24.4672, "lon": 54.6031},
    "Japanese Grand Prix": {"lat": 34.8431, "lon": 136.541}
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* [Mantenha todo o seu CSS aqui] */
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_data(endpoint):
    url = f"https://api.jolpi.ca/ergast/f1/2026/{endpoint}.json"
    try:
        r = requests.get(url, verify=False, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

# ── STANDINGS ───────────────────────────────────────
TEAM_COLORS = {
    "Mercedes":        "#00D2BE",
    "Ferrari":         "#E8002D",
    "Red Bull":        "#3671C6",
    "McLaren":         "#FF8000",
    "Aston Martin":    "#358C75",
    "Alpine F1 Team":  "#FF87BC",
    "Williams":        "#64C4FF",
    "RB F1 Team":      "#6692FF",
    "Kick Sauber":     "#52E252",
    "Haas F1 Team":    "#B6BABD",
    "Audi":            "#C0121B",
    "Cadillac F1 Team": "#CC0000",
}

FLAG_URLS = {
    "British":       "https://flagcdn.com/w40/gb.png",
    "Dutch":         "https://flagcdn.com/w40/nl.png",
    "Italian":       "https://flagcdn.com/w40/it.png",
    "Spanish":       "https://flagcdn.com/w40/es.png",
    "French":        "https://flagcdn.com/w40/fr.png",
    "Finnish":       "https://flagcdn.com/w40/fi.png",
    "Australian":    "https://flagcdn.com/w40/au.png",
    "German":        "https://flagcdn.com/w40/de.png",
    "Canadian":      "https://flagcdn.com/w40/ca.png",
    "Japanese":      "https://flagcdn.com/w40/jp.png",
    "Monegasque":    "https://flagcdn.com/w40/mc.png",
    "Chinese":       "https://flagcdn.com/w40/cn.png",
    "Danish":        "https://flagcdn.com/w40/dk.png",
    "New Zealander": "https://flagcdn.com/w40/nz.png",
    "Thai":          "https://flagcdn.com/w40/th.png",
    "Brazilian":     "https://flagcdn.com/w40/br.png",
    "Argentine":     "https://flagcdn.com/w40/ar.png",
    "Austrian":      "https://flagcdn.com/w40/at.png",
    "Mexican":       "https://flagcdn.com/w40/mx.png",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #07070F; color: #E8E8E8; }
.stApp, [data-testid="stAppViewContainer"] { background: #07070F; }
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #0D0D1A; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 100% !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; }
.hero-wrap { background: linear-gradient(135deg, #0D0010 0%, #07070F 55%, #100005 100%); border-bottom: 2px solid #E10600; padding: 2.5rem 2rem 2rem; margin-bottom: 2rem; position: relative; overflow: hidden; }
.hero-wrap::before { content: "F1"; position: absolute; right: -1rem; top: -1.5rem; font-family: 'Rajdhani', sans-serif; font-size: 11rem; font-weight: 700; color: rgba(225,6,0,0.04); line-height: 1; pointer-events: none; }
.hero-title { font-family: 'Rajdhani', sans-serif; font-size: 3rem; font-weight: 700; letter-spacing: 0.04em; color: #FFFFFF !important;   /* força branco sólido */ line-height: 1; margin: 0;}
.hero-title .year { color: #E10600; /* Apenas o ano em vermelho */}
.hero-sub { font-size: 0.75rem; font-weight: 500; letter-spacing: 0.2em; text-transform: uppercase; color: #666; margin: 0 0 0.4rem 0; }
.section-label { font-family: 'Rajdhani', sans-serif; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; color: #E10600; margin-bottom: 0.25rem; }
.section-title { font-family: 'Rajdhani', sans-serif; font-size: 1.65rem; font-weight: 700; color: #FFF; margin: 0 0 1rem 0; letter-spacing: 0.02em; }
.driver-card { background: #0F0F1C; border: 1px solid #1C1C2E; border-radius: 8px; display: flex; align-items: center; margin-bottom: 0.45rem; transition: border-color 0.2s, transform 0.15s; min-height: 68px; }
.driver-card:hover { border-color: #30304A; transform: translateX(4px); }
.card-accent { width: 4px; min-width: 4px; align-self: stretch; min-height: 68px; border-radius: 8px 0 0 8px; flex-shrink: 0; }
.card-pos { font-family: 'Rajdhani', sans-serif; font-size: 1.5rem; font-weight: 700; color: rgba(255,255,255,0.7); /* mais claro, legível */}
.card-pos.top3 { color: rgba(255,255,255,1); /* top 3 bem destacados */}
.card-info { flex: 1; padding: 0 0.8rem; min-width: 0; }
.card-name { font-family: 'Rajdhani', sans-serif; font-size: 1rem; font-weight: 600; color: #FFF; letter-spacing: 0.03em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.2; }
.card-meta { display: flex; align-items: center; gap: 0.45rem; margin-top: 0.2rem; }
.card-flag { height: 12px; border-radius: 1px; flex-shrink: 0; display: block; }
.card-team { font-size: 0.7rem; color: #777; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-pts { font-family: 'Rajdhani', sans-serif; font-size: 1.5rem; font-weight: 700; color: #FFF; padding: 0 1.1rem; flex-shrink: 0; line-height: 1.1; text-align: right; }
.card-pts-label { display: block; font-size: 0.58rem; font-weight: 400; color: #444; text-transform: uppercase; letter-spacing: 0.12em; text-align: right; }
.ctor-row { background: #0F0F1C; border: 1px solid #1C1C2E; border-radius: 8px; display: flex; align-items: center; margin-bottom: 0.4rem; transition: border-color 0.2s; min-height: 56px; }
.ctor-row:hover { border-color: #30304A; }
.ctor-pos { font-size: 1.25rem; font-weight: 700; color: rgba(255,255,255,0.15);}
.ctor-name { font-family: 'Rajdhani', sans-serif; font-size: 0.9rem; font-weight: 600; color: #FFF; letter-spacing: 0.03em; flex: 1; padding: 0 0.8rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ctor-pts { font-family: 'Rajdhani', sans-serif; font-size: 1.25rem; font-weight: 700; color: #FFF; padding: 0 1rem; flex-shrink: 0; line-height: 1.1; text-align: right; }
.ctor-pts small { display: block; font-size: 0.55rem; font-weight: 400; color: #444; text-transform: uppercase; letter-spacing: 0.1em; }
.f1-divider { border: none; border-top: 1px solid #181826; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_data(endpoint):
    url = f"https://api.jolpi.ca/ergast/f1/2026/{endpoint}.json"
    try:
        r = requests.get(url, verify=False, timeout=10)
        if r.status_code == 200: return r.json()
    except Exception: pass
    return None

def flag_url(nat): return FLAG_URLS.get(nat)
def team_color(team): return TEAM_COLORS.get(team, "#3A3A5A")
def safe_html(text): return str(text).replace('"', "&quot;").replace("'", "&#39;").replace("<", "&lt;").replace(">", "&gt;")



# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-wrap">'
    '<p class="hero-sub">FIA Formula One World Championship</p>'
    '<h1 class="hero-title">Season <span class="year">2026</span> Hub</h1>'
    '</div>',
    unsafe_allow_html=True
)
# ── STANDINGS ─────────────────────────────────────────────────────────────────
col_drivers, col_ctors = st.columns([3, 2], gap="large")

with col_drivers:
    st.markdown('<div class="section-label">Championship</div><div class="section-title">Driver Standings</div>', unsafe_allow_html=True)
    data_drivers = fetch_data("driverStandings")
    standings = data_drivers["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"] if data_drivers else []
    for d in standings:
        pos, fname, gname, nat = int(d["position"]), d["Driver"]["familyName"], d["Driver"]["givenName"], d["Driver"].get("nationality", "")
        team, pts, color = d["Constructors"][0]["name"], int(d["points"]), team_color(d["Constructors"][0]["name"])
        flag = flag_url(nat)
        flag_block = f'<img class="card-flag" src="{flag}" alt="{safe_html(nat)}">' if flag else ""
        st.markdown(f'''<div class="driver-card"><div class="card-accent" style="background:{color};"></div><div class="card-pos {'top3' if pos<=3 else ''}">{pos}</div><div class="card-info"><div class="card-name">{safe_html(gname + " " + fname)}</div><div class="card-meta">{flag_block}<span class="card-team">{safe_html(team)}</span></div></div><div class="card-pts">{pts}<span class="card-pts-label">PTS</span></div></div>''', unsafe_allow_html=True)

with col_ctors:
    st.markdown('<div class="section-label">Championship</div><div class="section-title">Constructor Standings</div>', unsafe_allow_html=True)
    data_const = fetch_data("constructorStandings")
    ctor_standings = data_const["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"] if data_const else []
    for c in ctor_standings:
        pos, name, pts, color = int(c["position"]), c["Constructor"]["name"], int(c["points"]), team_color(c["Constructor"]["name"])
        st.markdown(f'''<div class="ctor-row"><div class="card-accent" style="background:{color}; min-height:56px; border-radius:8px 0 0 8px;"></div><div class="ctor-pos">{pos}</div><div class="ctor-name">{safe_html(name)}</div><div class="ctor-pts">{pts}<small>PTS</small></div></div>''', unsafe_allow_html=True)

# ── DADOS FIXOS PARA GARANTIR O FUNCIONAMENTO (FALLBACK) ─────────────────────
# Se a API falhar, usaremos esta lista para o calendário
FALLBACK_RACES = [
    {
        "raceName": "Bahrain Grand Prix",
        "date": "2026-03-06", "time": "15:00:00Z",
        "Circuit": {
            "circuitName": "Bahrain International Circuit",
            "Location": {"locality": "Sakhir", "country": "Bahrain"}
        }
    },
    {
        "raceName": "Saudi Arabian Grand Prix",
        "date": "2026-03-20", "time": "17:00:00Z",
        "Circuit": {
            "circuitName": "Jeddah Corniche Circuit",
            "Location": {"locality": "Jeddah", "country": "Saudi Arabia"}
        }
    },
    {
        "raceName": "Australian Grand Prix",
        "date": "2026-04-03", "time": "05:00:00Z",
        "Circuit": {
            "circuitName": "Albert Park Circuit",
            "Location": {"locality": "Melbourne", "country": "Australia"}
        }
    },
    {
        "raceName": "Chinese Grand Prix",
        "date": "2026-04-17", "time": "08:00:00Z",
        "Circuit": {
            "circuitName": "Shanghai International Circuit",
            "Location": {"locality": "Shanghai", "country": "China"}
        }
    },
    {
        "raceName": "Japanese Grand Prix",
        "date": "2026-04-24", "time": "05:00:00Z",
        "Circuit": {
            "circuitName": "Suzuka Circuit",
            "Location": {"locality": "Suzuka", "country": "Japan"}
        }
    },
    {
        "raceName": "Miami Grand Prix",
        "date": "2026-05-01", "time": "20:00:00Z",
        "Circuit": {
            "circuitName": "Miami International Autodrome",
            "Location": {"locality": "Miami", "country": "USA"}
        }
    },
    {
        "raceName": "Emilia Romagna Grand Prix",
        "date": "2026-05-15", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Autodromo Enzo e Dino Ferrari",
            "Location": {"locality": "Imola", "country": "Italy"}
        }
    },
    {
        "raceName": "Monaco Grand Prix",
        "date": "2026-05-22", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Circuit de Monaco",
            "Location": {"locality": "Monte Carlo", "country": "Monaco"}
        }
    },
    {
        "raceName": "Spanish Grand Prix",
        "date": "2026-06-05", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Circuit de Barcelona-Catalunya",
            "Location": {"locality": "Barcelona", "country": "Spain"}
        }
    },
    {
        "raceName": "Canadian Grand Prix",
        "date": "2026-06-19", "time": "18:00:00Z",
        "Circuit": {
            "circuitName": "Circuit Gilles Villeneuve",
            "Location": {"locality": "Montreal", "country": "Canada"}
        }
    },
    {
        "raceName": "British Grand Prix",
        "date": "2026-07-05", "time": "14:00:00Z",
        "Circuit": {
            "circuitName": "Silverstone Circuit",
            "Location": {"locality": "Silverstone", "country": "UK"}
        }
    },
    {
        "raceName": "Austrian Grand Prix",
        "date": "2026-07-10", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Red Bull Ring",
            "Location": {"locality": "Spielberg", "country": "Austria"}
        }
    },
    {
        "raceName": "Hungarian Grand Prix",
        "date": "2026-07-24", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Hungaroring",
            "Location": {"locality": "Budapest", "country": "Hungary"}
        }
    },
    {
        "raceName": "Belgian Grand Prix",
        "date": "2026-07-31", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Circuit de Spa-Francorchamps",
            "Location": {"locality": "Spa-Francorchamps", "country": "Belgium"}
        }
    },
    {
        "raceName": "Dutch Grand Prix",
        "date": "2026-08-28", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Circuit Zandvoort",
            "Location": {"locality": "Zandvoort", "country": "Netherlands"}
        }
    },
    {
        "raceName": "Italian Grand Prix",
        "date": "2026-09-04", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Autodromo Nazionale Monza",
            "Location": {"locality": "Monza", "country": "Italy"}
        }
    },
    {
        "raceName": "Azerbaijan Grand Prix",
        "date": "2026-09-18", "time": "11:00:00Z",
        "Circuit": {
            "circuitName": "Baku City Circuit",
            "Location": {"locality": "Baku", "country": "Azerbaijan"}
        }
    },
    {
        "raceName": "Singapore Grand Prix",
        "date": "2026-10-02", "time": "12:00:00Z",
        "Circuit": {
            "circuitName": "Marina Bay Street Circuit",
            "Location": {"locality": "Singapore", "country": "Singapore"}
        }
    },
    {
        "raceName": "United States Grand Prix",
        "date": "2026-10-16", "time": "19:00:00Z",
        "Circuit": {
            "circuitName": "Circuit of the Americas",
            "Location": {"locality": "Austin", "country": "USA"}
        }
    },
    {
        "raceName": "Mexico City Grand Prix",
        "date": "2026-10-23", "time": "20:00:00Z",
        "Circuit": {
            "circuitName": "Autódromo Hermanos Rodríguez",
            "Location": {"locality": "Mexico City", "country": "Mexico"}
        }
    },
    {
        "raceName": "São Paulo Grand Prix",
        "date": "2026-11-06", "time": "18:00:00Z",
        "Circuit": {
            "circuitName": "Autódromo José Carlos Pace",
            "Location": {"locality": "São Paulo", "country": "Brazil"}
        }
    },
    {
        "raceName": "Las Vegas Grand Prix",
        "date": "2026-11-21", "time": "06:00:00Z",
        "Circuit": {
            "circuitName": "Las Vegas Strip Circuit",
            "Location": {"locality": "Las Vegas", "country": "USA"}
        }
    },
    {
        "raceName": "Qatar Grand Prix",
        "date": "2026-12-04", "time": "17:00:00Z",
        "Circuit": {
            "circuitName": "Lusail International Circuit",
            "Location": {"locality": "Lusail", "country": "Qatar"}
        }
    },
    {
        "raceName": "Abu Dhabi Grand Prix",
        "date": "2026-12-11", "time": "13:00:00Z",
        "Circuit": {
            "circuitName": "Yas Marina Circuit",
            "Location": {"locality": "Abu Dhabi", "country": "UAE"}
        }
    }
]


# ── CARREGAMENTO INTELIGENTE ────────────────────────────────────────────────
st.markdown('<hr class="f1-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Calendar</div><div class="section-title">World Circuit · F1 2026</div>', unsafe_allow_html=True)
data_cal = fetch_data("schedule")
# Se falhar, usa a lista fixa
races = data_cal['MRData']['RaceTable']['Races'] if data_cal else FALLBACK_RACES

map_list = []
fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_br)

# Lógica robusta de identificação do próximo GP
proximo_gp_nome = None
for r in races:
    dt = pd.to_datetime(f"{r['date']} {r.get('time', '00:00:00Z').replace('Z', '')}", utc=True).tz_convert('America/Sao_Paulo')
    if dt > agora:
        proximo_gp_nome = r['raceName']
        break

# Montagem do DataFrame
for gp_name, coords in FULL_CALENDAR.items():
    status = "Upcoming"
    data_formatada = "TBA"
    for r in races:
        if r['raceName'] == gp_name:
            dt = pd.to_datetime(f"{r['date']} {r.get('time', '00:00:00Z').replace('Z', '')}", utc=True).tz_convert('America/Sao_Paulo')
            data_formatada = dt.strftime('%d/%m %H:%M')
            if gp_name == proximo_gp_nome: status = "Next GP"
            elif dt < agora: status = "Completed"
            break
    map_list.append({"Grand Prix": gp_name, "lat": coords['lat'], "lon": coords['lon'], "Status": status, "Date": data_formatada})

df_map = pd.DataFrame(map_list)

# Renderização do Card
if proximo_gp_nome:
    proximo_race = next((r for r in races if r['raceName'] == proximo_gp_nome), None)
    dados = df_map[df_map['Grand Prix'] == proximo_gp_nome].iloc[0]

    circuito, local, country = "TBA", "TBA", None
    hora_local, hora_sp = "TBA", "TBA"

    if proximo_race and 'Circuit' in proximo_race:
        circuito = proximo_race['Circuit'].get('circuitName', "TBA")
        loc = proximo_race['Circuit'].get('Location', {})
        local = f"{loc.get('locality','TBA')}, {loc.get('country','TBA')}"
        country = loc.get('country')

        # Converte datas
        dt_utc = pd.to_datetime(
            f"{proximo_race['date']} {proximo_race.get('time','00:00:00Z').replace('Z','')}",
            utc=True
        )

        # Hora em São Paulo
        hora_sp = dt_utc.tz_convert('America/Sao_Paulo').strftime('%d/%m %H:%M')

        # Hora local do circuito (mapa de fusos simplificado)
        tz_map = {
            "Bahrain": "Asia/Bahrain", "Saudi Arabia": "Asia/Riyadh", "Australia": "Australia/Melbourne",
            "China": "Asia/Shanghai", "Japan": "Asia/Tokyo", "USA": "America/New_York",
            "Italy": "Europe/Rome", "Monaco": "Europe/Monaco", "Spain": "Europe/Madrid",
            "Canada": "America/Toronto", "Austria": "Europe/Vienna", "UK": "Europe/London",
            "Hungary": "Europe/Budapest", "Belgium": "Europe/Brussels", "Netherlands": "Europe/Amsterdam",
            "Azerbaijan": "Asia/Baku", "Singapore": "Asia/Singapore", "Mexico": "America/Mexico_City",
            "Brazil": "America/Sao_Paulo", "Qatar": "Asia/Qatar", "UAE": "Asia/Dubai"
        }
        tz_local = tz_map.get(country)
        if tz_local:
            hora_local = dt_utc.tz_convert(tz_local).strftime('%d/%m %H:%M')

    # Bandeira
    flag_img = ""
    if country:
        flag_code = COUNTRY_FLAGS.get(country, "").lower()
        if flag_code:
            flag_img = f'<img src="https://flagcdn.com/w40/{flag_code}.png" style="height:16px; margin-right:6px;">'

    # Renderiza o card
    st.markdown(f"""
        <div class="next-race-card">
            <div class="next-race-title">{dados['Grand Prix']}</div>
            <div style="color: #00E676; font-weight: 700;">NEXT GP</div>
            <div>📍 {circuito} — {local}</div>
            <div>{flag_img}{country if country else ""}</div>
            <div>🕒 Local: {hora_local}</div>
            <div>🕒 São Paulo: {hora_sp} BRT</div>
        </div>
    """, unsafe_allow_html=True)

# 4. Mapa mais "ajustado" e profissional
fig = px.scatter_mapbox(
    df_map, 
    lat="lat", 
    lon="lon", 
    color="Status",
    hover_name="Grand Prix", 
    hover_data={"Date": True, "Status": True, "lat": False, "lon": False},
    color_discrete_map={
        "Completed": "#757575", 
        "Upcoming": "#FF4B4B", 
        "Next GP": "#00E676"
    },
    zoom=1.3,           # Ajustado levemente para melhor equilíbrio
    height=550          # Um pouco mais de altura dá mais respiro
)

# Substitua o bloco do fig.update_layout por este:

fig.update_layout(
    mapbox_style="carto-darkmatter",
    margin={"r":0, "t":0, "l":0, "b":0},
    # Centraliza o mapa globalmente com um zoom mais confortável
    mapbox=dict(
        center=dict(lat=20, lon=10), 
        zoom=1.4
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom", 
        y=0.03, 
        xanchor="center", 
        x=0.5,
        bgcolor="rgba(0,0,0,0.5)",
        font=dict(color="#FAFAFA", size=12)
    )
)

# Adiciona um padding extra para que os pontos não fiquem colados na borda
fig.update_geos(fitbounds="locations")

st.plotly_chart(fig, use_container_width=True)
