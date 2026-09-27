import streamlit as st
import pandas as pd
import requests
import urllib3
import plotly.express as px
from datetime import datetime
import pytz

# Desativa alertas de certificados SSL não verificados para a API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =====================================================================
# CONFIGURAÇÃO GERAL
# =====================================================================
st.set_page_config(
    page_title="F1 2026 · Season Hub",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================================
# CONSTANTES E DICIONÁRIOS DE APOIO
# =====================================================================
COUNTRY_FLAGS = {
    "Bahrain": "bh", "Saudi Arabia": "sa", "Australia": "au", "China": "cn",
    "USA": "us", "Italy": "it", "Monaco": "mc", "Spain": "es", "Canada": "ca",
    "Austria": "at", "UK": "gb", "Hungary": "hu", "Belgium": "be",
    "Netherlands": "nl", "Azerbaijan": "az", "Singapore": "sg",
    "Mexico": "mx", "Brazil": "br", "Qatar": "qa", "UAE": "ae", "Japan": "jp"
}

TEAM_COLORS = {
    "Mercedes": "#00D2BE", "Ferrari": "#E8002D", "Red Bull": "#3671C6",
    "McLaren": "#FF8000", "Aston Martin": "#358C75", "Alpine F1 Team": "#FF87BC",
    "Williams": "#64C4FF", "RB F1 Team": "#6692FF", "Kick Sauber": "#52E252",
    "Haas F1 Team": "#B6BABD", "Audi": "#C0121B", "Cadillac F1 Team": "#CC0000",
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

CIRCUIT_MAPS = {
    "Bahrain International Circuit": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Bahrain_International_Circuit_-_Layout.svg",
    "Jeddah Corniche Circuit": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Jeddah_Circuit_Map.svg",
    "Albert Park Circuit": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Albert_Park_Circuit_2022.svg",
    "Suzuka International Racing Course": "https://upload.wikimedia.org/wikipedia/commons/d/dd/Suzuka_circuit_map-en.svg",
    "Shanghai International Circuit": "https://upload.wikimedia.org/wikipedia/commons/5/58/Shanghai_International_Circuit.svg",
    "Miami International Autodrome": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Miami_International_Autodrome.svg",
    "Circuit Gilles Villeneuve": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Circuit_Gilles_Villeneuve_2012.svg",
    "Circuit de Monaco": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Circuit_Monaco.svg",
    "Circuit de Barcelona-Catalunya": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Circuit_de_Barcelona-Catalunya_%282021%29.svg",
    "Red Bull Ring": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Red_Bull_Ring.svg",
    "Silverstone Circuit": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Silverstone_Circuit_2020.svg",
    "Circuit de Spa-Francorchamps": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Spa-Francorchamps_2007.svg",
    "Hungaroring": "https://upload.wikimedia.org/wikipedia/commons/9/91/Hungaroring.svg",
    "Circuit Zandvoort": "https://upload.wikimedia.org/wikipedia/commons/6/66/Circuit_Zandvoort_track_layout.svg",
    "Autodromo Nazionale Monza": "https://upload.wikimedia.org/wikipedia/commons/6/69/Autodromo_Nazionale_Monza_in_2010_%28italiano%29.svg",
    "Baku City Circuit": "https://upload.wikimedia.org/wikipedia/commons/c/c2/Baku_Formula_1_circuit_map.svg",
    "Marina Bay Street Circuit": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Marina_Bay_Street_Circuit_2023.svg",
    "Circuit of the Americas": "https://upload.wikimedia.org/wikipedia/commons/3/33/Circuit_of_the_Americas.svg",
    "Autodromo Hermanos Rodriguez": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Aut%C3%B3dromo_Hermanos_Rodr%C3%ADguez_layout_%282015%29.svg",
    "Autodromo Jose Carlos Pace": "https://upload.wikimedia.org/wikipedia/commons/6/64/Aut%C3%B3dromo_Jos%C3%A9_Carlos_Pace_layout.svg",
    "Las Vegas Strip Circuit": "https://upload.wikimedia.org/wikipedia/commons/2/23/Las_Vegas_Strip_Circuit_map.svg",
    "Losail International Circuit": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Losail_International_Circuit_2023.svg",
    "Yas Marina Circuit": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Yas_Marina_Circuit_2021.svg",
    "Sepang International Circuit": "https://upload.wikimedia.org/wikipedia/commons/6/67/Sepang.svg",
    "MADRING Sur": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/IFEMA_Madrid_Circuit_layout_1.svg/1024px-IFEMA_Madrid_Circuit_layout_1.svg.png"
}

# ── DADOS FIXOS PARA GARANTIR O FUNCIONAMENTO (FALLBACK INTEGRAL) ────────────
FALLBACK_RACES = [
    {
        'raceName': 'Australian Grand Prix', 'date': '2026-03-08', 'time': '05:00:00Z',
        'Circuit': {'circuitName': 'Albert Park Circuit', 'Location': {'locality': 'Melbourne', 'country': 'Australia', 'lat': '-37.8497', 'long': '144.968'}},
        'laps': 58, 'circuitLengthKm': 5.278, 'raceDistanceKm': 306.124,
        'lapRecord': {'time': '1:19.813', 'driver': 'Sergio Perez', 'year': 2023},
        'sessions': {'Race': '2026-03-08T05:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Chinese Grand Prix', 'date': '2026-03-15', 'time': '07:00:00Z',
        'Circuit': {'circuitName': 'Shanghai International Circuit', 'Location': {'locality': 'Shanghai', 'country': 'China', 'lat': '31.3389', 'long': '121.2222'}},
        'laps': 56, 'circuitLengthKm': 5.451, 'raceDistanceKm': 305.066,
        'lapRecord': {'time': '1:32.238', 'driver': 'Michael Schumacher', 'year': 2004},
        'sessions': {'Race': '2026-03-15T07:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Japanese Grand Prix', 'date': '2026-03-29', 'time': '05:00:00Z',
        'Circuit': {'circuitName': 'Suzuka International Racing Course', 'Location': {'locality': 'Suzuka', 'country': 'Japan', 'lat': '34.8431', 'long': '136.541'}},
        'laps': 53, 'circuitLengthKm': 5.807, 'raceDistanceKm': 307.471,
        'lapRecord': {'time': '1:30.983', 'driver': 'Lewis Hamilton', 'year': 2019},
        'sessions': {'Race': '2026-03-29T05:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Miami Grand Prix', 'date': '2026-05-03', 'time': '20:00:00Z',
        'Circuit': {'circuitName': 'Miami International Autodrome', 'Location': {'locality': 'Miami Gardens', 'country': 'USA', 'lat': '25.9581', 'long': '-80.2389'}},
        'laps': 57, 'circuitLengthKm': 5.412, 'raceDistanceKm': 308.326,
        'lapRecord': {'time': '1:29.708', 'driver': 'Max Verstappen', 'year': 2023},
        'sessions': {'Race': '2026-05-03T20:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Canadian Grand Prix', 'date': '2026-05-24', 'time': '18:00:00Z',
        'Circuit': {'circuitName': 'Circuit Gilles Villeneuve', 'Location': {'locality': 'Montreal', 'country': 'Canada', 'lat': '45.5081', 'long': '-73.5228'}},
        'laps': 70, 'circuitLengthKm': 4.361, 'raceDistanceKm': 305.27,
        'lapRecord': {'time': '1:13.078', 'driver': 'Valtteri Bottas', 'year': 2019},
        'sessions': {'Race': '2026-05-24T18:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Monaco Grand Prix', 'date': '2026-06-07', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'Circuit de Monaco', 'Location': {'locality': 'Monte Carlo', 'country': 'Monaco', 'lat': '43.7347', 'long': '7.4206'}},
        'laps': 78, 'circuitLengthKm': 3.337, 'raceDistanceKm': 260.286,
        'lapRecord': {'time': '1:12.909', 'driver': 'Lewis Hamilton', 'year': 2021},
        'sessions': {'Race': '2026-06-07T13:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Spanish Grand Prix (Barcelona)', 'date': '2026-06-14', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'Circuit de Barcelona-Catalunya', 'Location': {'locality': 'Barcelona', 'country': 'Spain', 'lat': '41.5700', 'long': '2.2611'}},
        'laps': 66, 'circuitLengthKm': 4.657, 'raceDistanceKm': 307.236,
        'lapRecord': {'time': '1:16.330', 'driver': 'Max Verstappen', 'year': 2023},
        'sessions': {'Race': '2026-06-14T13:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Austrian Grand Prix', 'date': '2026-06-28', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'Red Bull Ring', 'Location': {'locality': 'Spielberg', 'country': 'Austria', 'lat': '47.2197', 'long': '14.7647'}},
        'laps': 71, 'circuitLengthKm': 4.318, 'raceDistanceKm': 306.452,
        'lapRecord': {'time': '1:05.619', 'driver': 'Carlos Sainz', 'year': 2020},
        'sessions': {'Race': '2026-06-28T13:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'British Grand Prix', 'date': '2026-07-05', 'time': '14:00:00Z',
        'Circuit': {'circuitName': 'Silverstone Circuit', 'Location': {'locality': 'Silverstone', 'country': 'UK', 'lat': '52.0786', 'long': '-1.0169'}},
        'laps': 52, 'circuitLengthKm': 5.891, 'raceDistanceKm': 306.198,
        'lapRecord': {'time': '1:27.097', 'driver': 'Max Verstappen', 'year': 2020},
        'sessions': {'Race': '2026-07-05T14:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Belgian Grand Prix', 'date': '2026-07-19', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'Circuit de Spa-Francorchamps', 'Location': {'locality': 'Spa', 'country': 'Belgium', 'lat': '50.4372', 'long': '5.9714'}},
        'laps': 44, 'circuitLengthKm': 7.004, 'raceDistanceKm': 308.052,
        'lapRecord': {'time': '1:46.286', 'driver': 'Valtteri Bottas', 'year': 2018},
        'sessions': {'Race': '2026-07-19T13:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Hungarian Grand Prix', 'date': '2026-07-26', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'Hungaroring', 'Location': {'locality': 'Budapest', 'country': 'Hungary', 'lat': '47.5789', 'long': '19.2486'}},
        'laps': 70, 'circuitLengthKm': 4.381, 'raceDistanceKm': 306.63,
        'lapRecord': {'time': '1:16.627', 'driver': 'Lewis Hamilton', 'year': 2020},
        'sessions': {'Race': '2026-07-26T13:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Dutch Grand Prix', 'date': '2026-08-23', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'Circuit Zandvoort', 'Location': {'locality': 'Zandvoort', 'country': 'Netherlands', 'lat': '52.3888', 'long': '4.5409'}},
        'laps': 72, 'circuitLengthKm': 4.259, 'raceDistanceKm': 306.587,
        'lapRecord': {'time': '1:11.097', 'driver': 'Lewis Hamilton', 'year': 2021},
        'sessions': {'Race': '2026-08-23T13:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Italian Grand Prix', 'date': '2026-09-06', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'Autodromo Nazionale Monza', 'Location': {'locality': 'Monza', 'country': 'Italy', 'lat': '45.6156', 'long': '9.2811'}},
        'laps': 53, 'circuitLengthKm': 5.793, 'raceDistanceKm': 306.72,
        'lapRecord': {'time': '1:21.046', 'driver': 'Rubens Barrichello', 'year': 2004},
        'sessions': {'Race': '2026-09-06T13:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Spanish Grand Prix (Madrid)', 'date': '2026-09-13', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'MADRING Sur', 'Location': {'locality': 'Madrid', 'country': 'Spain', 'lat': '40.4168', 'long': '-3.7038'}},
        'laps': 55, 'circuitLengthKm': 5.4, 'raceDistanceKm': 297.0,
        'lapRecord': {'time': '1:31.000', 'driver': 'TBA', 'year': 2026},
        'sessions': {'Race': '2026-09-13T13:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Azerbaijan Grand Prix', 'date': '2026-09-26', 'time': '11:00:00Z',
        'Circuit': {'circuitName': 'Baku City Circuit', 'Location': {'locality': 'Baku', 'country': 'Azerbaijan', 'lat': '40.3725', 'long': '49.8533'}},
        'laps': 51, 'circuitLengthKm': 6.003, 'raceDistanceKm': 306.049,
        'lapRecord': {'time': '1:43.370', 'driver': 'Charles Leclerc', 'year': 2019},
        'sessions': {'Race': '2026-09-26T11:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Malaysian Grand Prix (Bahrain GP in Malaysia)', 'date': '2026-10-04', 'time': '07:00:00Z',
        'Circuit': {'circuitName': 'Sepang International Circuit', 'Location': {'locality': 'Sepang', 'country': 'Malaysia', 'lat': '2.7608', 'long': '101.7381'}},
        'laps': 56, 'circuitLengthKm': 5.543, 'raceDistanceKm': 310.408,
        'lapRecord': {'time': '1:34.223', 'driver': 'Juan Pablo Montoya', 'year': 2004},
        'sessions': {'Race': '2026-10-04T07:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Singapore Grand Prix', 'date': '2026-10-11', 'time': '12:00:00Z',
        'Circuit': {'circuitName': 'Marina Bay Street Circuit', 'Location': {'locality': 'Singapore', 'country': 'Singapore', 'lat': '1.2891', 'long': '103.864'}},
        'laps': 62, 'circuitLengthKm': 4.94, 'raceDistanceKm': 306.143,
        'lapRecord': {'time': '1:35.785', 'driver': 'Lewis Hamilton', 'year': 2023},
        'sessions': {'Race': '2026-10-11T12:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'United States Grand Prix', 'date': '2026-10-25', 'time': '19:00:00Z',
        'Circuit': {'circuitName': 'Circuit of the Americas', 'Location': {'locality': 'Austin', 'country': 'USA', 'lat': '30.1328', 'long': '-97.6411'}},
        'laps': 56, 'circuitLengthKm': 5.513, 'raceDistanceKm': 308.405,
        'lapRecord': {'time': '1:36.169', 'driver': 'Charles Leclerc', 'year': 2019},
        'sessions': {'Race': '2026-10-25T19:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Mexican Grand Prix', 'date': '2026-11-01', 'time': '20:00:00Z',
        'Circuit': {'circuitName': 'Autodromo Hermanos Rodriguez', 'Location': {'locality': 'Mexico City', 'country': 'Mexico', 'lat': '19.4042', 'long': '-99.0907'}},
        'laps': 71, 'circuitLengthKm': 4.304, 'raceDistanceKm': 305.354,
        'lapRecord': {'time': '1:17.774', 'driver': 'Valtteri Bottas', 'year': 2021},
        'sessions': {'Race': '2026-11-01T20:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Brazilian Grand Prix', 'date': '2026-11-08', 'time': '17:00:00Z',
        'Circuit': {'circuitName': 'Autodromo Jose Carlos Pace', 'Location': {'locality': 'Sao Paulo', 'country': 'Brazil', 'lat': '-23.7036', 'long': '-46.6997'}},
        'laps': 71, 'circuitLengthKm': 4.309, 'raceDistanceKm': 305.879,
        'lapRecord': {'time': '1:10.540', 'driver': 'Valtteri Bottas', 'year': 2018},
        'sessions': {'Race': '2026-11-08T17:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Las Vegas Grand Prix', 'date': '2026-11-21', 'time': '06:00:00Z',
        'Circuit': {'circuitName': 'Las Vegas Strip Circuit', 'Location': {'locality': 'Las Vegas', 'country': 'USA', 'lat': '36.1147', 'long': '-115.1728'}},
        'laps': 50, 'circuitLengthKm': 6.201, 'raceDistanceKm': 310.05,
        'lapRecord': {'time': '1:35.490', 'driver': 'Oscar Piastri', 'year': 2023},
        'sessions': {'Race': '2026-11-21T06:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Qatar Grand Prix', 'date': '2026-11-29', 'time': '16:00:00Z',
        'Circuit': {'circuitName': 'Losail International Circuit', 'Location': {'locality': 'Doha', 'country': 'Qatar', 'lat': '25.4888', 'long': '51.4542'}},
        'laps': 57, 'circuitLengthKm': 5.419, 'raceDistanceKm': 308.827,
        'lapRecord': {'time': '1:24.319', 'driver': 'Max Verstappen', 'year': 2023},
        'sessions': {'Race': '2026-11-29T16:00:00Z'}, 'weatherForecast': 'TBA'
    },
    {
        'raceName': 'Abu Dhabi Grand Prix', 'date': '2026-12-06', 'time': '13:00:00Z',
        'Circuit': {'circuitName': 'Yas Marina Circuit', 'Location': {'locality': 'Abu Dhabi', 'country': 'UAE', 'lat': '24.4672', 'long': '54.6031'}},
        'laps': 58, 'circuitLengthKm': 5.281, 'raceDistanceKm': 306.283,
        'lapRecord': {'time': '1:26.103', 'driver': 'Max Verstappen', 'year': 2021},
        'sessions': {'Race': '2026-12-06T13:00:00Z'}, 'weatherForecast': 'TBA'
    }
]

# =====================================================================
# CLASSES E FUNÇÕES DE NEGÓCIO
# =====================================================================
@st.cache_data(ttl=3600)
def fetch_api_data(endpoint: str) -> dict:
    """Busca dados da API Ergast via Jolpi com fallback para erros."""
    url = f"https://api.jolpi.ca/ergast/f1/2026/{endpoint}.json"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Silencia o log no UI principal e retorna None para acionar o fallback
        return None

def safe_html(text: str) -> str:
    """Sanitiza strings para injeção segura em HTML."""
    return str(text).replace('"', "&quot;").replace("'", "&#39;").replace("<", "&lt;").replace(">", "&gt;")

def parse_utc_datetime(date_str: str, time_str: str) -> datetime:
    """Converte strings de data e hora da API para objeto datetime em UTC."""
    clean_time = time_str.replace('Z', '') if time_str else '00:00:00'
    return pd.to_datetime(f"{date_str} {clean_time}", utc=True)

# =====================================================================
# ESTILIZAÇÃO CSS
# =====================================================================
def inject_custom_css():
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

    /* Componentes Gerais */
    .section-label { font-family: 'Rajdhani', sans-serif; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; color: #E10600; margin-bottom: 0.25rem; }
    .section-title { font-family: 'Rajdhani', sans-serif; font-size: 1.65rem; font-weight: 700; color: #FFF; margin: 0 0 1rem 0; letter-spacing: 0.02em; }
    .f1-divider { border: none; border-top: 1px solid #181826; margin: 2rem 0; }

    /* Cards Classificação */
    .driver-card, .ctor-row { background: #0F0F1C; border: 1px solid #1C1C2E; border-radius: 8px; display: flex; align-items: center; margin-bottom: 0.45rem; transition: border-color 0.2s, transform 0.15s; }
    .driver-card { min-height: 68px; flex-wrap: wrap; }
    .ctor-row { min-height: 56px; }
    .driver-card:hover, .ctor-row:hover { border-color: #30304A; transform: translateX(4px); }
    .card-accent { width: 4px; min-width: 4px; align-self: stretch; border-radius: 8px 0 0 8px; flex-shrink: 0; }
    .card-pos, .ctor-pos { font-family: 'Rajdhani', sans-serif; font-weight: 700; text-align: center; flex-shrink: 0; }
    .card-pos { font-size: 1.5rem; color: rgba(255,255,255,0.13); width: 3rem; }
    .ctor-pos { font-size: 1.25rem; color: rgba(255,255,255,0.15); width: 2.8rem; }
    .card-pos.top3 { color: rgba(255,255,255,0.45); }
    
    .card-info { flex: 1; padding: 0 0.8rem; min-width: 0; }
    .card-name, .ctor-name { font-family: 'Rajdhani', sans-serif; font-weight: 600; color: #FFF; letter-spacing: 0.03em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .card-name { font-size: 1rem; line-height: 1.2; }
    .ctor-name { font-size: 0.9rem; flex: 1; padding: 0 0.8rem; }
    
    .card-meta { display: flex; align-items: center; gap: 0.45rem; margin-top: 0.2rem; }
    .card-flag { height: 12px; border-radius: 1px; flex-shrink: 0; display: block; }
    .card-team { font-size: 0.7rem; color: #777; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    
    .card-pts, .ctor-pts { font-family: 'Rajdhani', sans-serif; font-size: 1.5rem; font-weight: 700; color: #FFF; padding: 0 1.1rem; flex-shrink: 0; line-height: 1.1; text-align: right; }
    .ctor-pts { font-size: 1.25rem; padding: 0 1rem; }
    .card-pts-label, .ctor-pts small { display: block; font-weight: 400; color: #444; text-transform: uppercase; letter-spacing: 0.12em; text-align: right; }
    .card-pts-label { font-size: 0.58rem; }
    .ctor-pts small { font-size: 0.55rem; letter-spacing: 0.1em; }

    /* Next Race Card & Map */
    .next-race-card { background: #0F0F1C; border: 1px solid #1C1C2E; border-radius: 8px; padding: 1.5rem; color: #FFFFFF; font-size: 0.95rem; display: flex; flex-direction: column; gap: 0.4rem; }
    .next-race-title { font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; font-weight: 700; color: #FFF; margin-bottom: 0.2rem;}
    .next-race-sub { color: #E10600; font-weight: 700; letter-spacing: 0.1em; font-size: 0.85rem; margin-bottom: 0.5rem; text-transform: uppercase;}
    .race-details { background: #131322; border: 1px solid #1C1C2E; border-radius: 8px; padding: 1rem; margin-top: 1rem; color: #CCCCCC;}
    .race-details summary { font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; font-weight: 600; color: #00D2BE; cursor: pointer; outline: none; margin-bottom: 0.5rem; }
    .race-details summary:hover { color: #00E676; }
    
    /* Configuração da imagem do circuito para fundo escuro */
    .circuit-map-img { background-color: #E8E8E8; border-radius: 6px; padding: 10px; width: 100%; margin-top: 10px; margin-bottom: 10px; object-fit: contain; max-height: 180px; }
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# RENDERIZAÇÃO DE COMPONENTES
# =====================================================================
def render_hero():
    st.markdown(
        '<div class="hero-wrap">'
        '<p class="hero-sub">FIA Formula One World Championship</p>'
        '<h1 class="hero-title">Season <span class="year">2026</span> Hub</h1>'
        '</div>',
        unsafe_allow_html=True
    )

def render_standings():
    col_drivers, col_ctors = st.columns([3, 2], gap="large")

    # Pilotos
    with col_drivers:
        st.markdown('<div class="section-label">Championship</div><div class="section-title">Driver Standings</div>', unsafe_allow_html=True)
        data_drivers = fetch_api_data("driverStandings")
        
        try:
            standings = data_drivers["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
        except (TypeError, KeyError, IndexError):
            standings = []
            st.info("Aguardando início da temporada para dados de pilotos.")

        for d in standings:
            pos = int(d.get("position", 0))
            fname = safe_html(d["Driver"].get("familyName", ""))
            gname = safe_html(d["Driver"].get("givenName", ""))
            nat = d["Driver"].get("nationality", "")
            
            team_data = d.get("Constructors", [{}])[0]
            team = safe_html(team_data.get("name", "Unknown"))
            pts = safe_html(d.get("points", "0"))
            color = TEAM_COLORS.get(team_data.get("name"), "#3A3A5A")
            
            code = FLAG_URLS.get(nat)
            flag_img = f'<img class="card-flag" src="https://flagcdn.com/w40/{code}.png" alt="{nat}">' if code else ""
            
            st.markdown(f'''
                <div class="driver-card">
                    <div class="card-accent" style="background:{color};"></div>
                    <div class="card-pos {'top3' if pos<=3 else ''}">{pos}</div>
                    <div class="card-info">
                        <div class="card-name">{gname} {fname}</div>
                        <div class="card-meta">{flag_img}<span class="card-team">{team}</span></div>
                    </div>
                    <div class="card-pts">{pts}<span class="card-pts-label">PTS</span></div>
                </div>
            ''', unsafe_allow_html=True)

    # Construtores
    with col_ctors:
        st.markdown('<div class="section-label">Championship</div><div class="section-title">Constructor Standings</div>', unsafe_allow_html=True)
        data_const = fetch_api_data("constructorStandings")
        
        try:
            ctor_standings = data_const["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
        except (TypeError, KeyError, IndexError):
            ctor_standings = []
            st.info("Aguardando início da temporada para construtores.")

        for c in ctor_standings:
            pos = int(c.get("position", 0))
            name = safe_html(c["Constructor"].get("name", ""))
            pts = safe_html(c.get("points", "0"))
            color = TEAM_COLORS.get(c["Constructor"].get("name"), "#3A3A5A")
            
            st.markdown(f'''
                <div class="ctor-row">
                    <div class="card-accent" style="background:{color};"></div>
                    <div class="ctor-pos">{pos}</div>
                    <div class="ctor-name">{name}</div>
                    <div class="ctor-pts">{pts}<small>PTS</small></div>
                </div>
            ''', unsafe_allow_html=True)


def render_calendar_and_map():
    st.markdown('<hr class="f1-divider">', unsafe_allow_html=True)
    
    data_cal = fetch_api_data("schedule")
    races = data_cal['MRData']['RaceTable']['Races'] if data_cal and 'RaceTable' in data_cal['MRData'] else FALLBACK_RACES

    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_br)
    
    proximo_race = None
    
    # Descobre qual a próxima corrida
    for r in races:
        try:
            dt_utc = parse_utc_datetime(r.get('date', ''), r.get('time', ''))
            data_br = dt_utc.tz_convert(fuso_br)
            if data_br > agora:
                proximo_race = r
                break
        except Exception:
            continue

    col_map, col_next = st.columns([2, 1], gap="medium")

    # Renderiza o Card da Próxima Corrida (Com Mapa do Circuito)
    with col_next:
        st.markdown('<div class="section-label">On Track</div><div class="section-title">Next Event</div>', unsafe_allow_html=True)
        
        if proximo_race:
            try:
                circuito = safe_html(proximo_race.get('Circuit', {}).get('circuitName', "TBA"))
                loc = proximo_race.get('Circuit', {}).get('Location', {})
                country = loc.get('country', "TBA")
                local = safe_html(f"{loc.get('locality','TBA')}, {country}")
                
                # Resgate do mapa (SVG) correspondente ao circuito
                circuit_svg_url = CIRCUIT_MAPS.get(proximo_race.get('Circuit', {}).get('circuitName', ""))
                svg_html = f'<img class="circuit-map-img" src="{circuit_svg_url}" alt="{circuito} layout">' if circuit_svg_url else ""

                # Datas e Timezones
                dt_utc = parse_utc_datetime(proximo_race.get('date', ''), proximo_race.get('time', ''))
                hora_sp = dt_utc.tz_convert(fuso_br).strftime('%d/%m %H:%M')
                
                tz_local = TZ_MAP.get(country)
                hora_local = dt_utc.tz_convert(tz_local).strftime('%d/%m %H:%M') if tz_local else "TBA"

                # Bandeira
                flag_code = COUNTRY_FLAGS.get(country)
                flag_img = f'<img class="card-flag" style="display:inline; height:14px;" src="https://flagcdn.com/w40/{flag_code}.png">' if flag_code else ""

                # Dados Extra (Tratados com `.get()` seguro para API e Fallback)
                laps = safe_html(proximo_race.get('laps', 'TBA'))
                dist = safe_html(proximo_race.get('raceDistanceKm', 'TBA'))
                rec_time = safe_html(proximo_race.get('lapRecord', {}).get('time', 'TBA'))
                rec_driver = safe_html(proximo_race.get('lapRecord', {}).get('driver', 'TBA'))

                st.markdown(f"""
                    <div class="next-race-card">
                        <div class="next-race-sub">NEXT GRAND PRIX</div>
                        <div class="next-race-title">{safe_html(proximo_race.get('raceName', 'TBA'))}</div>
                        <div>📍 {circuito}</div>
                        <div>{flag_img} {local}</div>
                        <hr style="border-color: #1C1C2E; margin: 0.5rem 0;">
                        <div>🕒 Local: <strong>{hora_local}</strong></div>
                        <div>🕒 Brasília: <strong style="color:#00D2BE;">{hora_sp} BRT</strong></div>
                    </div>

                    <details class="race-details">
                      <summary>Detalhes do Circuito</summary>
                      {svg_html}
                      <div>🏎️ <strong>Voltas:</strong> {laps}</div>
                      <div>📏 <strong>Distância:</strong> {dist} km</div>
                      <div>⏱️ <strong>Recorde:</strong> {rec_time} ({rec_driver})</div>
                    </details>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error("Erro ao processar detalhes da próxima corrida.")
        else:
            st.info("Temporada encerrada ou sem eventos futuros registrados.")

    # Renderiza o Mapa-Múndi Plotly
    with col_map:
        st.markdown('<div class="section-label">Calendar</div><div class="section-title">World Circuit · F1 2026</div>', unsafe_allow_html=True)
        
        map_data = []
        for r in races:
            try:
                dt_utc = parse_utc_datetime(r.get('date', ''), r.get('time', ''))
                horario_brasilia = dt_utc.tz_convert(fuso_br)
                data_formatada = horario_brasilia.strftime('%d/%m/%Y %H:%M')
                
                is_next = (proximo_race and r.get('raceName') == proximo_race.get('raceName'))
                if is_next:
                    status = "PRÓXIMO GP"
                elif horario_brasilia < agora:
                    status = "Corrida Realizada"
                else:
                    status = "Futura"
                    
                location = r.get('Circuit', {}).get('Location', {})
                lat = float(location.get('lat', 0))
                lon = float(location.get('long', 0))
                
                if lat != 0 and lon != 0:
                    map_data.append({
                        "Etapa": f"R{r.get('round', '?')}",
                        "Grande Prêmio": r.get('raceName', 'Unknown'),
                        "Circuito": r.get('Circuit', {}).get('circuitName', 'Unknown'),
                        "Local": f"{location.get('locality', '')}, {location.get('country', '')}",
                        "Data/Hora (BR)": data_formatada,
                        "lat": lat,
                        "lon": lon,
                        "Status": status
                    })
            except Exception:
                continue
                
        if map_data:
            df_map = pd.DataFrame(map_data)
            df_map["Tamanho_Marcador"] = df_map['Status'].map({"Corrida Realizada": 8, "PRÓXIMO GP": 18, "Futura": 8})
            
            fig = px.scatter_map(
                df_map, lat="lat", lon="lon", color="Status",
                color_discrete_map={"Corrida Realizada": "#757575", "PRÓXIMO GP": "#00E676", "Futura": "#FF4B4B"},
                size="Tamanho_Marcador", size_max=18, hover_name="Grande Prêmio",
                hover_data={"Etapa": True, "Circuito": True, "Local": True, "Data/Hora (BR)": True, "Status": True, "Tamanho_Marcador": False, "lat": False, "lon": False},
                zoom=1.1, height=520
            )
            
            fig.update_layout(
                map_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0},
                paper_bgcolor="#07070F", plot_bgcolor="#07070F",
                legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.02, font=dict(color="#FAFAFA"), bgcolor="rgba(7, 7, 15, 0.7)")
            )
            
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning("Coordenadas do calendário indisponíveis no momento.")

# =====================================================================
# FUNÇÃO PRINCIPAL (ENTRY POINT)
# =====================================================================
def main():
    inject_custom_css()
    render_hero()
    render_standings()
    render_calendar_and_map()

if __name__ == "__main__":
    main()
