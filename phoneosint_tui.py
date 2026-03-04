#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║         PHONE OSINT v2.0 — HACKER EDITION                ║
║   phonenumbers · Holehe · Google dorking · Geoapify      ║
║   Claude AI threat assessment — curses TUI               ║
╚══════════════════════════════════════════════════════════╝
"""

import curses
import json
import os
import re
import sys
import time
import random
import threading
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone

# ── Color pairs ───────────────────────────────────────────────────────────────
C_NORMAL   = 1
C_GREEN    = 2
C_CYAN     = 3
C_RED      = 4
C_YELLOW   = 5
C_MAGENTA  = 6
C_SELECTED = 7
C_BORDER   = 8
C_HEADER   = 9
C_DIM      = 10

MATRIX_CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ01"

BANNER = [
    "  ██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗ ██████╗ ███████╗██╗███╗   ██╗████████╗",
    "  ██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝",
    "  ██████╔╝███████║██║   ██║██╔██╗ ██║█████╗  ██║   ██║███████╗██║██╔██╗ ██║   ██║   ",
    "  ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝  ██║   ██║╚════██║██║██║╚██╗██║   ██║   ",
    "  ██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗╚██████╔╝███████║██║██║ ╚████║   ██║   ",
    "  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   ",
    "  ─────────────── O S I N T  v2.0 ── H A C K E R  E D I T I O N ───────────────────",
]

MENU_ITEMS = [
    ("[1]", "PHONE LOOKUP",       "Análisis completo de número telefónico"),
    ("[2]", "GOOGLE DORKING",     "Búsqueda automática en Google"),
    ("[3]", "HOLEHE CHECK",       "Detectar servicios con email"),
    ("[4]", "GEOAPIFY MAP",       "Geolocalizar región del número"),
    ("[5]", "BATCH ANALYSIS",     "Analizar múltiples números"),
    ("[6]", "AI SUMMARY",         "Claude AI — análisis completo"),
    ("[7]", "VIEW REPORTS",       "Ver reportes guardados"),
]

REPORTS_DIR = Path("osint_reports")
REPORTS_DIR.mkdir(exist_ok=True)


# ── Utilities ─────────────────────────────────────────────────────────────────

def safe_addstr(win, y, x, text, attr=0):
    try:
        h, w = win.getmaxyx()
        if y < 0 or y >= h or x < 0:
            return
        max_len = w - x - 1
        if max_len <= 0:
            return
        win.addstr(y, x, str(text)[:max_len], attr)
    except curses.error:
        pass


def draw_box(win, y, x, h, w, color, title=""):
    attr = curses.color_pair(color)
    try:
        win.attron(attr)
        win.addch(y,     x,     curses.ACS_ULCORNER)
        win.addch(y,     x+w-1, curses.ACS_URCORNER)
        win.addch(y+h-1, x,     curses.ACS_LLCORNER)
        win.addch(y+h-1, x+w-1, curses.ACS_LRCORNER)
        for i in range(1, w-1):
            win.addch(y,     x+i, curses.ACS_HLINE)
            win.addch(y+h-1, x+i, curses.ACS_HLINE)
        for i in range(1, h-1):
            win.addch(y+i, x,     curses.ACS_VLINE)
            win.addch(y+i, x+w-1, curses.ACS_VLINE)
        win.attroff(attr)
        if title:
            t  = f" {title} "
            tx = x + (w - len(t)) // 2
            safe_addstr(win, y, tx, t, attr | curses.A_BOLD)
    except curses.error:
        pass


def draw_header(stdscr, title="PHONE OSINT v2.0"):
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(C_HEADER) | curses.A_BOLD)
    stdscr.addstr(0, 0, " " * (w - 1))
    safe_addstr(stdscr, 0, 2, f"[ {title} ]")
    now = time.strftime("%H:%M:%S")
    safe_addstr(stdscr, 0, w - 12, f"[ {now} ]")
    stdscr.attroff(curses.color_pair(C_HEADER) | curses.A_BOLD)


def draw_footer(stdscr, hints="[Q] Quit  [↑↓] Navigate  [Enter] Select"):
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(C_HEADER))
    stdscr.addstr(h-1, 0, " " * (w - 1))
    safe_addstr(stdscr, h-1, 2, hints)
    stdscr.attroff(curses.color_pair(C_HEADER))


def input_box(stdscr, prompt, width=60):
    h, w   = stdscr.getmaxyx()
    bh, bw = 5, width + 4
    by     = h // 2 - 2
    bx     = w // 2 - bw // 2
    popup  = curses.newwin(bh, bw, by, bx)
    draw_box(popup, 0, 0, bh, bw, C_CYAN, "INPUT")
    safe_addstr(popup, 1, 2, prompt[:bw-4], curses.color_pair(C_YELLOW))
    safe_addstr(popup, 2, 2, ">" + " " * (bw-4), curses.color_pair(C_GREEN))
    popup.refresh()
    curses.echo()
    curses.curs_set(1)
    try:
        result = popup.getstr(2, 3, width-2).decode("utf-8", errors="ignore").strip()
    except Exception:
        result = ""
    finally:
        curses.noecho()
        curses.curs_set(0)
    return result


def show_log_screen(stdscr, title: str, lines: list,
                    hints="[Q/ESC] Back  [↑↓] Scroll  [S] Save"):
    h, w    = stdscr.getmaxyx()
    scroll  = 0
    visible = h - 4

    while True:
        stdscr.erase()
        draw_header(stdscr, title)
        draw_footer(stdscr, hints)
        draw_box(stdscr, 1, 0, h-2, w, C_BORDER)

        for i in range(visible):
            idx = scroll + i
            if idx >= len(lines):
                break
            line = lines[idx]
            if any(x in line for x in ["ERROR", "✗", "CRITICAL", "ALERT"]):
                attr = curses.color_pair(C_RED)
            elif any(x in line for x in ["⚠", "WARNING", "FOUND", "MATCH"]):
                attr = curses.color_pair(C_YELLOW)
            elif any(x in line for x in ["✓", "OK", "CLEAN", "✔"]):
                attr = curses.color_pair(C_GREEN)
            elif any(x in line for x in ["══", ">>>"]):
                attr = curses.color_pair(C_CYAN) | curses.A_BOLD
            else:
                attr = curses.color_pair(C_GREEN)
            safe_addstr(stdscr, 2+i, 2, line[:w-4], attr)

        if len(lines) > visible:
            pct     = scroll / max(1, len(lines) - visible)
            bar_pos = int(pct * (visible - 1))
            for i in range(visible):
                ch = "█" if i == bar_pos else "│"
                safe_addstr(stdscr, 2+i, w-2, ch, curses.color_pair(C_DIM))

        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):
            break
        elif key == curses.KEY_UP and scroll > 0:
            scroll -= 1
        elif key == curses.KEY_DOWN and scroll < len(lines) - visible:
            scroll += 1
        elif key == curses.KEY_PPAGE:
            scroll = max(0, scroll - visible)
        elif key == curses.KEY_NPAGE:
            scroll = min(max(0, len(lines) - visible), scroll + visible)
        elif key in (ord('s'), ord('S')):
            ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
            out  = REPORTS_DIR / f"report_{ts}.txt"
            out.write_text("\n".join(lines))
            lines.append(f"  ✓ Saved → {out}")


def loading_screen(stdscr, title: str, task_fn, *args):
    h, w    = stdscr.getmaxyx()
    result  = [None]
    done    = [False]

    def run():
        result[0] = task_fn(*args)
        done[0]   = True

    t = threading.Thread(target=run)
    t.start()

    spinners   = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    matrix_pos = [random.randint(0, h) for _ in range(w)]
    frame      = 0

    while not done[0]:
        stdscr.erase()
        draw_header(stdscr, title)

        for col in range(min(w-1, len(matrix_pos))):
            y  = matrix_pos[col]
            ch = random.choice(MATRIX_CHARS)
            if 0 < y < h-1:
                try:
                    attr = curses.color_pair(C_GREEN)
                    if random.random() > 0.85:
                        attr |= curses.A_BOLD
                    stdscr.addstr(y, col, ch, attr)
                    if y > 1:
                        stdscr.addstr(y-1, col, ch, curses.color_pair(C_DIM))
                except curses.error:
                    pass
            matrix_pos[col] = (y + 1) % (h - 1)

        bw, bh = 44, 7
        by = h // 2 - bh // 2
        bx = w // 2 - bw // 2
        draw_box(stdscr, by, bx, bh, bw, C_CYAN, "SCANNING")

        spinner = spinners[frame % len(spinners)]
        msg     = f"{spinner}  Gathering intel... {spinner}"
        safe_addstr(stdscr, by+2, bx + (bw - len(msg)) // 2, msg,
                    curses.color_pair(C_GREEN) | curses.A_BOLD)
        dots = "." * ((frame // 3) % 4)
        safe_addstr(stdscr, by+4, bx+2, f"  Please wait{dots:<4}",
                    curses.color_pair(C_DIM))

        stdscr.refresh()
        time.sleep(0.08)
        frame += 1

    t.join()
    return result[0]


# ── OSINT Modules ─────────────────────────────────────────────────────────────

def phone_lookup(number: str) -> list:
    lines = [f">>> PHONE LOOKUP: {number}", ""]
    try:
        import phonenumbers
        from phonenumbers import geocoder, carrier, timezone as pntimezone

        parsed = phonenumbers.parse(number)
        valid  = phonenumbers.is_valid_number(parsed)
        possible = phonenumbers.is_possible_number(parsed)

        country  = geocoder.description_for_number(parsed, "es")
        operator = carrier.name_for_number(parsed, "es")
        timezones = pntimezone.time_zones_for_number(parsed)
        fmt_intl  = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        fmt_e164  = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        num_type  = phonenumbers.number_type(parsed)

        type_names = {
            0: "FIXED_LINE", 1: "MOBILE", 2: "FIXED_OR_MOBILE",
            3: "TOLL_FREE",  4: "PREMIUM_RATE", 6: "VOIP",
            7: "PERSONAL",   8: "PAGER", 27: "UNKNOWN"
        }

        lines += [
            "══ NÚMERO INFO ══════════════════════════════",
            f"  Número:       {fmt_intl}",
            f"  E164:         {fmt_e164}",
            f"  País código:  +{parsed.country_code}",
            f"  Válido:       {'✓ SÍ' if valid else '✗ NO'}",
            f"  Posible:      {'✓ SÍ' if possible else '✗ NO'}",
            "",
            "══ GEOLOCALIZACIÓN ══════════════════════════",
            f"  País/Región:  {country or 'No disponible'}",
            f"  Operador:     {operator or 'No disponible'}",
            f"  Tipo línea:   {type_names.get(num_type, 'UNKNOWN')}",
            f"  Timezone:     {', '.join(timezones) if timezones else 'N/A'}",
            "",
            "══ GOOGLE DORKS (copia y pega) ══════════════",
            f'  "{number}"',
            f'  "{fmt_intl}" site:linkedin.com',
            f'  "{fmt_intl}" site:facebook.com',
            f'  "{fmt_intl}" email',
            f'  "{number}" filetype:pdf',
            f'  "{number}" "@gmail.com" OR "@hotmail.com"',
            "",
            "✓ Phone lookup complete",
        ]

    except ImportError:
        lines.append("ERROR: phonenumbers not installed. Run: pip install phonenumbers")
    except Exception as e:
        lines.append(f"ERROR: {e}")
    return lines


def google_dork(query: str) -> list:
    lines = [f">>> GOOGLE DORKING: {query}", ""]
    try:
        dorks = [
            f'"{query}"',
            f'"{query}" email',
            f'"{query}" site:linkedin.com',
            f'"{query}" site:facebook.com',
            f'"{query}" site:twitter.com OR site:x.com',
            f'"{query}" site:instagram.com',
            f'"{query}" "@gmail.com" OR "@yahoo.com" OR "@hotmail.com"',
            f'"{query}" filetype:pdf OR filetype:doc',
            f'intext:"{query}" contact',
            f'"{query}" whatsapp',
        ]

        lines += [
            "══ DORKS GENERADOS ══════════════════════════",
            "  Copia y pega en Google / DuckDuckGo:",
            "",
        ]

        for i, dork in enumerate(dorks, 1):
            encoded = urllib.parse.quote(dork)
            lines.append(f"  [{i:02d}] {dork}")
            lines.append(f"       → https://google.com/search?q={encoded}")
            lines.append("")

        # DuckDuckGo scraping (no API key needed)
        lines += ["══ BÚSQUEDA AUTOMÁTICA (DuckDuckGo) ═════════"]
        try:
            encoded_q = urllib.parse.quote(f'"{query}" email')
            url       = f"https://html.duckduckgo.com/html/?q={encoded_q}"
            req       = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            # Extract results
            results = re.findall(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', html)
            snippets = re.findall(r'class="result__snippet">(.*?)</span>', html)

            # Extract emails found
            emails = list(set(re.findall(
                r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html
            )))

            if results:
                lines.append(f"  Resultados encontrados: {len(results)}")
                for r in results[:5]:
                    clean = re.sub(r'<[^>]+>', '', r).strip()
                    if clean:
                        lines.append(f"  → {clean[:70]}")
            else:
                lines.append("  Sin resultados automáticos")

            if emails:
                lines += ["", "  ⚠ EMAILS ENCONTRADOS:"]
                for email in emails[:10]:
                    if len(email) > 5 and "." in email.split("@")[-1]:
                        lines.append(f"    ✔ {email}")

        except Exception as e:
            lines.append(f"  Búsqueda automática falló: {e}")
            lines.append("  Usa los dorks manualmente en el navegador")

        lines += ["", "✓ Google dorking complete"]

    except Exception as e:
        lines.append(f"ERROR: {e}")
    return lines


def holehe_check(email: str) -> list:
    lines = [f">>> HOLEHE CHECK: {email}", ""]
    try:
        import subprocess
        result = subprocess.run(
            ["holehe", email, "--only-used"],
            capture_output=True, text=True, timeout=60
        )
        output = result.stdout + result.stderr

        if output:
            lines += ["══ SERVICIOS DETECTADOS ═════════════════════"]
            found = []
            for line in output.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if "[+]" in line or "✔" in line or "used" in line.lower():
                    found.append(line)
                    lines.append(f"  ✔ {line}")
                elif "[-]" in line or "not used" in line.lower():
                    pass  # Skip not used
                else:
                    lines.append(f"  {line}")

            lines += [
                "",
                f"  Total servicios detectados: {len(found)}",
                "",
                "✓ Holehe check complete",
            ]
        else:
            lines.append("  Sin output — verifica que holehe está instalado")
            lines.append("  Run: pip install holehe")

    except FileNotFoundError:
        lines += [
            "  ⚠ holehe no está instalado",
            "  Run: pip install holehe",
            "",
            "  Alternativa manual:",
            f"  → https://haveibeenpwned.com/account/{urllib.parse.quote(email)}",
        ]
    except Exception as e:
        lines.append(f"ERROR: {e}")
    return lines


def geoapify_lookup(number: str, api_key: str) -> list:
    lines = [f">>> GEOAPIFY LOOKUP: {number}", ""]
    try:
        import phonenumbers
        from phonenumbers import geocoder

        parsed  = phonenumbers.parse(number)
        country = geocoder.description_for_number(parsed, "en")

        if not country:
            lines.append("  No country info available for this number")
            return lines

        lines += [
            "══ GEOCODIFICACIÓN ══════════════════════════",
            f"  Buscando: {country}",
            "",
        ]

        # Geoapify geocoding API
        encoded = urllib.parse.quote(country)
        url     = (f"https://api.geoapify.com/v1/geocode/search"
                   f"?text={encoded}&apiKey={api_key}&limit=1")

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        features = data.get("features", [])
        if not features:
            lines.append(f"  No geocoding results for: {country}")
            return lines

        props = features[0].get("properties", {})
        coords = features[0].get("geometry", {}).get("coordinates", [])

        lines += [
            f"  País:       {props.get('country', 'N/A')}",
            f"  Ciudad:     {props.get('city', props.get('state', 'N/A'))}",
            f"  Estado:     {props.get('state', 'N/A')}",
            f"  Código:     {props.get('country_code', 'N/A').upper()}",
            f"  Continente: {props.get('continent', 'N/A')}",
        ]

        if coords and len(coords) >= 2:
            lon, lat = coords[0], coords[1]
            lines += [
                f"  Latitud:    {lat}",
                f"  Longitud:   {lon}",
                "",
                "══ MAPA ═════════════════════════════════════",
                f"  Google Maps: https://maps.google.com/?q={lat},{lon}",
                f"   OpenStreetMap: https://www.openstreetmap.org/?mlat={lat}&mlon={lon}",
            ]

        # Save HTML map
        if coords and len(coords) >= 2:
            html_map = _generate_map_html(number, lat, lon, props, api_key)
            out      = REPORTS_DIR / f"map_{number.replace('+','').replace(' ','_')}.html"
            out.write_text(html_map)
            lines += ["", f"  ✓ Mapa HTML guardado → {out}"]

        lines += ["", "✓ Geoapify lookup complete"]

    except ImportError:
        lines.append("ERROR: phonenumbers not installed")
    except Exception as e:
        lines.append(f"ERROR: {e}")
    return lines


def _generate_map_html(number: str, lat: float, lon: float,
                        props: dict, api_key: str) -> str:
    country = props.get('country', 'Unknown')
    city    = props.get('city', props.get('state', ''))
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Phone OSINT — {number}</title>
<style>
  body {{ margin:0; background:#0d1117; color:#c9d1d9; font-family:monospace; }}
  #map {{ width:100%; height:70vh; }}
  .info {{ padding:16px; background:#161b22; border-top:2px solid #21262d; }}
  h2 {{ color:#58a6ff; }}
  .badge {{ background:#1f6feb; color:#fff; padding:2px 8px; border-radius:4px;
            font-size:12px; margin:2px; display:inline-block; }}
</style>
<link rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
<div id="map"></div>
<div class="info">
  <h2>📍 Phone OSINT — {number}</h2>
  <span class="badge">🌍 {country}</span>
  <span class="badge">🏙 {city}</span>
  <span class="badge">📍 {lat:.4f}, {lon:.4f}</span>
  <p style="color:#8b949e;font-size:12px;margin-top:8px">
  ⚠ Esta ubicación corresponde a la región de registro del número,
  NO a la ubicación actual del dispositivo.
  </p>
</div>
<script>
  var map = L.map('map').setView([{lat}, {lon}], 6);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '© OpenStreetMap'
  }}).addTo(map);
  L.marker([{lat}, {lon}])
    .addTo(map)
    .bindPopup('<b>{number}</b><br>{country} — {city}')
    .openPopup();
</script>
</body>
</html>"""


def batch_analysis(filepath: str) -> list:
    lines = [f">>> BATCH ANALYSIS: {filepath}", ""]
    try:
        p = Path(filepath)
        if not p.exists():
            lines.append(f"ERROR: File not found: {filepath}")
            return lines

        numbers = []
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                numbers.append(line)

        lines += [
            f"  Numbers found: {len(numbers)}",
            "",
            "══ RESULTS ══════════════════════════════════",
        ]

        import phonenumbers
        from phonenumbers import geocoder, carrier

        results = []
        for num in numbers[:50]:  # cap at 50
            try:
                parsed   = phonenumbers.parse(num)
                valid    = phonenumbers.is_valid_number(parsed)
                country  = geocoder.description_for_number(parsed, "es")
                operator = carrier.name_for_number(parsed, "es")
                status   = "✓" if valid else "✗"
                lines.append(f"  {status} {num:<20} {country:<20} {operator}")
                results.append({
                    "number": num, "valid": valid,
                    "country": country, "operator": operator
                })
            except Exception as e:
                lines.append(f"  ✗ {num:<20} ERROR: {e}")

        # Save JSON
        out = REPORTS_DIR / f"batch_{int(time.time())}.json"
        out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        lines += ["", f"  ✓ Report saved → {out}", "", "✓ Batch analysis complete"]

    except ImportError:
        lines.append("ERROR: phonenumbers not installed")
    except Exception as e:
        lines.append(f"ERROR: {e}")
    return lines


def ai_summary(number: str, api_key: str) -> list:
    lines = [f">>> AI SUMMARY: {number}", ""]
    if not api_key:
        lines += [
            "ERROR: ANTHROPIC_API_KEY not set",
            "Set it with: export ANTHROPIC_API_KEY=sk-ant-...",
        ]
        return lines

    try:
        import phonenumbers
        from phonenumbers import geocoder, carrier, timezone as pntimezone

        parsed    = phonenumbers.parse(number)
        country   = geocoder.description_for_number(parsed, "en")
        operator  = carrier.name_for_number(parsed, "en")
        timezones = pntimezone.time_zones_for_number(parsed)
        valid     = phonenumbers.is_valid_number(parsed)
        fmt_intl  = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        prompt = f"""You are an OSINT analyst. Analyze this phone number and provide intelligence.

PHONE NUMBER: {fmt_intl}
VALID: {valid}
COUNTRY/REGION: {country}
OPERATOR: {operator}
TIMEZONES: {', '.join(timezones)}

Provide:
1. **Risk Assessment**: Is this number suspicious? (spam, scam, legitimate)
2. **Geographic Analysis**: What can we infer about the region?
3. **Operator Intelligence**: What does the carrier tell us?
4. **Recommended OSINT Steps**: Next steps to investigate this number
5. **Google Dorks**: Top 3 most effective search queries for this number

Be concise and technical. Format as a professional OSINT report."""

        payload = json.dumps({
            "model":      "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages":   [{"role": "user", "content": prompt}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type":      "application/json",
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        lines.append("  [*] Sending to Claude API...")
        lines.append("══ AI ANALYSIS ══════════════════════════════")

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())

        text = "".join(b.get("text","") for b in data.get("content",[])
                       if b.get("type") == "text")
        lines += text.split("\n")
        lines += ["", "✓ AI Summary complete"]

    except ImportError:
        lines.append("ERROR: phonenumbers not installed")
    except Exception as e:
        lines.append(f"ERROR: {e}")
    return lines


def view_reports() -> list:
    lines = [">>> SAVED REPORTS", ""]
    reports = list(REPORTS_DIR.glob("*.json")) + list(REPORTS_DIR.glob("*.txt"))
    if not reports:
        lines.append("  No reports found yet.")
        return lines
    lines.append(f"  Found {len(reports)} reports in {REPORTS_DIR}/")
    lines.append("")
    for r in sorted(reports, key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        size = r.stat().st_size
        mtime = datetime.fromtimestamp(r.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {mtime}  {r.name:<40} {size:>8,} bytes")
    return lines


# ── Main Menu ─────────────────────────────────────────────────────────────────

def handle_selection(stdscr, idx: int):
    geo_key = os.environ.get("GEOAPIFY_KEY", "")
    ai_key  = os.environ.get("ANTHROPIC_API_KEY", "")

    if idx == 0:  # Phone lookup
        number = input_box(stdscr, "Número telefónico (ej: +573001234567):", width=50)
        if number:
            lines = loading_screen(stdscr, "PHONE LOOKUP", phone_lookup, number)
            show_log_screen(stdscr, "PHONE LOOKUP", lines)

    elif idx == 1:  # Google dorking
        query = input_box(stdscr, "Número o dato a buscar:", width=50)
        if query:
            lines = loading_screen(stdscr, "GOOGLE DORKING", google_dork, query)
            show_log_screen(stdscr, "GOOGLE DORKING", lines)

    elif idx == 2:  # Holehe
        email = input_box(stdscr, "Email a verificar:", width=50)
        if email:
            lines = loading_screen(stdscr, "HOLEHE CHECK", holehe_check, email)
            show_log_screen(stdscr, "HOLEHE CHECK", lines)

    elif idx == 3:  # Geoapify
        if not geo_key:
            geo_key = input_box(stdscr, "Geoapify API Key (o setea GEOAPIFY_KEY en env):", width=60)
        if geo_key:
            number = input_box(stdscr, "Número telefónico (ej: +573001234567):", width=50)
            if number:
                lines = loading_screen(stdscr, "GEOAPIFY MAP", geoapify_lookup, number, geo_key)
                show_log_screen(stdscr, "GEOAPIFY MAP", lines)
        else:
            show_log_screen(stdscr, "ERROR", ["  ERROR: Geoapify API key required",
                                               "  Get free key at: geoapify.com"])

    elif idx == 4:  # Batch
        filepath = input_box(stdscr, "Ruta al archivo .txt con números:", width=60)
        if filepath:
            lines = loading_screen(stdscr, "BATCH ANALYSIS", batch_analysis, filepath)
            show_log_screen(stdscr, "BATCH ANALYSIS", lines)

    elif idx == 5:  # AI Summary
        if not ai_key:
            ai_key = input_box(stdscr, "Anthropic API Key:", width=65)
        number = input_box(stdscr, "Número telefónico (ej: +573001234567):", width=50)
        if number:
            lines = loading_screen(stdscr, "AI SUMMARY", ai_summary, number, ai_key)
            show_log_screen(stdscr, "AI SUMMARY", lines)

    elif idx == 6:  # View reports
        lines = view_reports()
        show_log_screen(stdscr, "REPORTS", lines)


def main_menu(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_NORMAL,   curses.COLOR_WHITE,   -1)
    curses.init_pair(C_GREEN,    curses.COLOR_GREEN,   -1)
    curses.init_pair(C_CYAN,     curses.COLOR_CYAN,    -1)
    curses.init_pair(C_RED,      curses.COLOR_RED,     -1)
    curses.init_pair(C_YELLOW,   curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_MAGENTA,  curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_SELECTED, curses.COLOR_BLACK,   curses.COLOR_GREEN)
    curses.init_pair(C_BORDER,   curses.COLOR_WHITE,   -1)
    curses.init_pair(C_HEADER,   curses.COLOR_BLACK,   curses.COLOR_CYAN)
    curses.init_pair(C_DIM,      curses.COLOR_GREEN,   -1)

    curses.curs_set(0)
    curses.noecho()
    stdscr.keypad(True)

    selected   = 0
    h, w       = stdscr.getmaxyx()
    matrix_pos = [random.randint(0, h) for _ in range(w)]

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        draw_header(stdscr)
        draw_footer(stdscr, "[↑↓] Navigate  [Enter/1-7] Select  [Q] Quit")

        # Banner
        banner_y = 1
        for i, line in enumerate(BANNER):
            color = C_GREEN if i < len(BANNER)-1 else C_CYAN
            attr  = curses.color_pair(color)
            if i < len(BANNER)-1:
                attr |= curses.A_BOLD
            safe_addstr(stdscr, banner_y+i, max(0, (w-len(line))//2), line, attr)

        menu_y = banner_y + len(BANNER) + 1
        menu_w = min(68, w-4)
        menu_x = (w - menu_w) // 2
        menu_h = len(MENU_ITEMS) + 2
        draw_box(stdscr, menu_y, menu_x, menu_h, menu_w, C_BORDER, "[ SELECT MODULE ]")

        for i, (key, name, desc) in enumerate(MENU_ITEMS):
            is_sel = (i == selected)
            y = menu_y + 1 + i
            x = menu_x + 2
            if is_sel:
                attr = curses.color_pair(C_SELECTED) | curses.A_BOLD
                safe_addstr(stdscr, y, menu_x+1, " " * (menu_w-2), attr)
                safe_addstr(stdscr, y, x, f"{key} {name:<22} {desc}", attr)
            else:
                safe_addstr(stdscr, y, x,   key,            curses.color_pair(C_YELLOW) | curses.A_BOLD)
                safe_addstr(stdscr, y, x+4, f"{name:<22}",  curses.color_pair(C_GREEN)  | curses.A_BOLD)
                safe_addstr(stdscr, y, x+27, desc,          curses.color_pair(C_DIM))

        # Status bar
        status_y = menu_y + menu_h + 1
        geo_ok   = bool(os.environ.get("GEOAPIFY_KEY"))
        ai_ok    = bool(os.environ.get("ANTHROPIC_API_KEY"))
        safe_addstr(stdscr, status_y, menu_x,
            f"  GEOAPIFY: {'✓' if geo_ok else '✗'}  CLAUDE_API: {'✓' if ai_ok else '✗'}",
            curses.color_pair(C_DIM))

        stdscr.refresh()
        stdscr.timeout(100)
        key = stdscr.getch()
        stdscr.timeout(-1)

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(MENU_ITEMS)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_ENTER, 10, 13):
            handle_selection(stdscr, selected)
        elif key in range(ord('1'), ord('7')+1):
            handle_selection(stdscr, key - ord('1'))
        elif key in (ord('q'), ord('Q')):
            break


def main():
    REPORTS_DIR.mkdir(exist_ok=True)
    curses.wrapper(main_menu)


if __name__ == "__main__":
    main()
