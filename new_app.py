
import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask, request, render_template_string
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN", "")
API_URL = "https://api.football-data.org/v4"
TZ = ZoneInfo("Africa/Algiers")

LEAGUES = {
    "PL": "Premier League",
    "PD": "La Liga",
    "SA": "Serie A",
    "BL1": "Bundesliga",
    "FL1": "Ligue 1",
    "CL": "Champions League",
    "DED": "Eredivisie",
    "PPL": "Primeira Liga",
    "BSA": "Brazil Serie A",
    "ELC": "Championship",
}

TEXT = {
    "ar": {
        "subtitle": "منصة كرة القدم الذكية",
        "live": "المباريات المباشرة",
        "today": "مباريات اليوم",
        "upcoming": "المباريات القادمة",
        "recent": "آخر النتائج",
        "refresh": "تحديث المباريات",
        "home": "الفريق الأول",
        "away": "الفريق الثاني",
        "analyze": "تحليل المباراة",
        "no_matches": "لا توجد مباريات في هذه الفترة.",
        "loading_error": "تعذر جلب المباريات. حاول لاحقاً.",
        "admin": "تواصل مع الإدارة",
        "disclaimer": "النتائج والتوقعات غير مضمونة.",
        "note": "هذا تحليل مبدئي وليس توقعاً من نموذج ذكاء اصطناعي مدرّب.",
    },
    "en": {
        "subtitle": "Smart Football Platform",
        "live": "Live Matches",
        "today": "Today's Matches",
        "upcoming": "Upcoming Matches",
        "recent": "Recent Results",
        "refresh": "Refresh Matches",
        "home": "Home Team",
        "away": "Away Team",
        "analyze": "Analyze Match",
        "no_matches": "No matches found for this period.",
        "loading_error": "Could not load matches. Try again later.",
        "admin": "Contact Admins",
        "disclaimer": "Results and predictions are not guaranteed.",
        "note": "This is a basic analysis, not a trained AI prediction.",
    },
    "fr": {
        "subtitle": "Plateforme de football intelligente",
        "live": "Matchs en direct",
        "today": "Matchs du jour",
        "upcoming": "Matchs à venir",
        "recent": "Derniers résultats",
        "refresh": "Actualiser les matchs",
        "home": "Équipe à domicile",
        "away": "Équipe visiteuse",
        "analyze": "Analyser le match",
        "no_matches": "Aucun match pour cette période.",
        "loading_error": "Impossible de charger les matchs.",
        "admin": "Contacter les administrateurs",
        "disclaimer": "Les résultats et pronostics ne sont pas garantis.",
        "note": "Analyse simple, sans modèle IA entraîné.",
    },
}

PAGE = r"""
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ direction }}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PREDIX | Football</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#080b12;color:#f4f6fb;font-family:Arial,sans-serif}
header{padding:22px 16px;background:#101622;border-bottom:1px solid #252d3c}
.wrap{max-width:1000px;margin:auto;padding:0 14px}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.logo{font-size:29px;font-weight:900;color:#41f5a1;letter-spacing:2px}
.sub{color:#aab4c5;margin-top:6px}
.lang a{color:#fff;text-decoration:none;border:1px solid #394354;padding:7px 10px;border-radius:8px;margin:2px;display:inline-block}
main{padding:22px 0}
select,button,input{padding:12px;border-radius:9px;border:1px solid #313b4d;background:#151d2b;color:#fff;font-size:15px}
button{background:#27d98a;color:#07110b;border:0;font-weight:bold;cursor:pointer}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}
.controls select{flex:1;min-width:180px}
h2{font-size:20px;margin-top:25px}
.section{background:#101622;border:1px solid #252d3c;border-radius:14px;padding:15px;margin:14px 0}
.match{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:13px 0;border-bottom:1px solid #273043}
.match:last-child{border-bottom:0}
.teams{flex:1;font-weight:bold}
.score{color:#41f5a1;font-size:18px;font-weight:bold;white-space:nowrap}
.meta{color:#9aa8bc;font-size:12px;margin-top:6px}
.tag{font-size:12px;color:#41f5a1}
.notice{color:#ffc66d;padding:10px 0}
footer{padding:25px 15px;text-align:center;color:#aab4c5;background:#101622;margin-top:30px}
footer a{color:#41f5a1;text-decoration:none;margin:6px;display:inline-block}
form.analysis{display:flex;gap:8px;flex-wrap:wrap}
form.analysis input{flex:1;min-width:130px}
@media(max-width:500px){.match{align-items:flex-start}.teams{font-size:14px}.score{font-size:16px}}
</style>
</head>
<body>
<header>
<div class="wrap top">
<div><div class="logo">⚽ PREDIX</div><div class="sub">{{ t.subtitle }}</div></div>
<div class="lang">
<a href="?lang=ar&league={{ league }}">العربية</a>
<a href="?lang=en&league={{ league }}">English</a>
<a href="?lang=fr&league={{ league }}">Français</a>
</div>
</div>
</header>
<main class="wrap">
<form class="controls" method="get">
<input type="hidden" name="lang" value="{{ lang }}">
<select name="league">
{% for code,name in leagues.items() %}
<option value="{{ code }}" {% if code == league %}selected{% endif %}>{{ name }}</option>
{% endfor %}
</select>
<button type="submit">{{ t.refresh }}</button>
</form>
{% if error %}<div class="notice">{{ error }}</div>{% endif %}
{% for key,title in sections %}
<section class="section">
<h2>{{ title }}</h2>
{% set items = groups[key] %}
{% if items %}
{% for m in items %}
<div class="match">
<div class="teams">
{{ m.homeTeam.name or 'TBD' }} <span class="tag">vs</span> {{ m.awayTeam.name or 'TBD' }}
<div class="meta">{{ m.utcDate|datetime_display }} · {{ m.status }}</div>
</div>
<div class="score">
{% if m.status in ['FINISHED','IN_PLAY','PAUSED','HALF_TIME'] %}
{{ m.score.fullTime.home if m.score.fullTime.home is not none else m.score.halfTime.home if m.score.halfTime.home is not none else '-' }}
-
{{ m.score.fullTime.away if m.score.fullTime.away is not none else m.score.halfTime.away if m.score.halfTime.away is not none else '-' }}
{% else %}—{% endif %}
</div>
</div>
{% endfor %}
{% else %}
<p class="meta">{{ t.no_matches }}</p>
{% endif %}
</section>
{% endfor %}
<section class="section">
<h2>{{ t.analyze }}</h2>
<form class="analysis" method="get">
<input type="hidden" name="lang" value="{{ lang }}">
<input type="hidden" name="league" value="{{ league }}">
<input name="home" placeholder="{{ t.home }}" required>
<input name="away" placeholder="{{ t.away }}" required>
<button type="submit">{{ t.analyze }}</button>
</form>
{% if analysis %}
<p>{{ analysis }}</p>
<p class="meta">{{ t.note }}</p>
{% endif %}
</section>
</main>
<footer>
<p>{{ t.disclaimer }}</p>
<p>{{ t.admin }}</p>
<a href="https://www.instagram.com/_mahdi20_10_/" target="_blank" rel="noopener">Instagram: @_mahdi20_10_</a>
<a href="https://www.instagram.com/rahli_120/" target="_blank" rel="noopener">Instagram: @rahli_120</a>
<p>© 2026 PREDIX</p>
</footer>
</body>
</html>
"""
@app.template_filter("datetime_display")
def datetime_display(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(TZ).strftime("%d/%m %H:%M")
    except Exception:
        return value


def fetch_matches(league):
    if not API_TOKEN:
        return None, "API_KEY_MISSING"

    now = datetime.now(TZ)
    start = (now.date() - timedelta(days=3)).isoformat()
    end = (now.date() + timedelta(days=7)).isoformat()

    try:
        response = requests.get(
            f"{API_URL}/competitions/{league}/matches",
            headers={"X-Auth-Token": API_TOKEN},
            params={"dateFrom": start, "dateTo": end},
            timeout=15
        )

        if response.status_code != 200:
            return None, f"HTTP_{response.status_code}"

        return response.json().get("matches", []), None

    except requests.RequestException:
        return None, "NETWORK_ERROR"


@app.route("/")
def index():
    lang = request.args.get("lang", "ar")
    if lang not in TEXT:
        lang = "ar"

    league = request.args.get("league", "PL")
    if league not in LEAGUES:
        league = "PL"

    t = TEXT[lang]
    groups = {
        "live": [],
        "today": [],
        "upcoming": [],
        "recent": []
    }
    error = None

    matches, err = fetch_matches(league)

    if err:
        if err == "API_KEY_MISSING":
            error = {
                "ar": "تحقق من ملف .env ومفتاح API.",
                "en": "Check your .env file and API token.",
                "fr": "Vérifiez le fichier .env et le jeton API."
            }[lang]
        elif err == "HTTP_403":
            error = t["loading_error"] + " (403)"
        elif err == "HTTP_429":
            error = {
                "ar": "طلبات كثيرة، حاول لاحقاً.",
                "en": "Too many requests. Try later.",
                "fr": "Trop de requêtes. Réessayez plus tard."
            }[lang]
        else:
            error = t["loading_error"]

    else:
        today = datetime.now(TZ).date()

        for m in matches:
            try:
                match_date = datetime.fromisoformat(
                    m["utcDate"].replace("Z", "+00:00")
                ).astimezone(TZ).date()
            except Exception:
                continue

            status = m.get("status", "")

            if status in ("IN_PLAY", "PAUSED", "HALF_TIME"):
                groups["live"].append(m)
            elif status == "FINISHED":
                if today - timedelta(days=3) <= match_date <= today:
                    groups["recent"].append(m)
            elif match_date == today:
                groups["today"].append(m)
            elif today < match_date <= today + timedelta(days=7):
                groups["upcoming"].append(m)

    home = request.args.get("home", "").strip()
    away = request.args.get("away", "").strip()
    analysis = None

    if home and away:
        analysis = f"{home} vs {away}"

    sections = [
        ("live", t["live"]),
        ("today", t["today"]),
        ("upcoming", t["upcoming"]),
        ("recent", t["recent"])
    ]

    return render_template_string(
        PAGE,
        lang=lang,
        direction="rtl" if lang == "ar" else "ltr",
        t=t,
        league=league,
        leagues=LEAGUES,
        groups=groups,
        sections=sections,
        error=error,
        analysis=analysis
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
