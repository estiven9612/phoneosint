#!/usr/bin/env python3
"""
Módulo de Inferencia por Zona Horaria.
Cruza la zona horaria del prefijo con patrones de actividad
para estimar la ubicación aproximada del usuario.
Solo para entornos controlados con autorización.
"""

import phonenumbers
from phonenumbers import timezone as ph_timezone, geocoder
import json
import sys
from datetime import datetime, timezone
import pytz


def get_timezones(phone: str) -> list:
    """Obtiene las zonas horarias asociadas al número."""
    try:
        parsed = phonenumbers.parse(phone, None)
        zones = ph_timezone.time_zones_for_number(parsed)
        return list(zones)
    except Exception as e:
        print(f"[!] Error: {e}")
        return []


def analyze_timezone(tz_name: str) -> dict:
    """Analiza una zona horaria y calcula la hora actual en ella."""
    try:
        tz = pytz.timezone(tz_name)
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(tz)

        offset = now_local.utcoffset()
        offset_hours = offset.total_seconds() / 3600

        # Determinar si es horario laboral, nocturno, etc.
        hour = now_local.hour
        if 6 <= hour < 12:
            periodo = "🌅 Mañana"
        elif 12 <= hour < 14:
            periodo = "☀️ Mediodía"
        elif 14 <= hour < 19:
            periodo = "🌤️ Tarde"
        elif 19 <= hour < 23:
            periodo = "🌆 Noche"
        else:
            periodo = "🌙 Madrugada"

        # Probabilidad de que el dispositivo esté activo
        if 8 <= hour < 23:
            actividad = "Alta probabilidad de actividad"
        elif 6 <= hour < 8:
            actividad = "Media probabilidad de actividad"
        else:
            actividad = "Baja probabilidad (probablemente durmiendo)"

        return {
            "zona_horaria": tz_name,
            "hora_actual_alli": now_local.strftime("%Y-%m-%d %H:%M:%S"),
            "dia_semana": now_local.strftime("%A"),
            "utc_offset": f"UTC{'+' if offset_hours >= 0 else ''}{offset_hours:.1f}",
            "periodo_del_dia": periodo,
            "estimacion_actividad": actividad,
        }
    except Exception as e:
        return {"zona_horaria": tz_name, "error": str(e)}


def infer_location_by_timezone(zones: list) -> dict:
    """
    Infiere ubicación aproximada cruzando múltiples zonas horarias.
    Si hay varias zonas, muestra el rango probable.
    """
    # Mapeo de zonas horarias a regiones geográficas aproximadas
    zone_to_region = {
        "America/Bogota": "Colombia 🇨🇴",
        "America/New_York": "Costa Este USA / Canadá 🇺🇸",
        "America/Chicago": "Centro USA 🇺🇸",
        "America/Denver": "Montañas USA 🇺🇸",
        "America/Los_Angeles": "Costa Oeste USA 🇺🇸",
        "America/Mexico_City": "México Centro 🇲🇽",
        "America/Caracas": "Venezuela 🇻🇪",
        "America/Lima": "Perú 🇵🇪",
        "America/Santiago": "Chile 🇨🇱",
        "America/Argentina/Buenos_Aires": "Argentina 🇦🇷",
        "America/Sao_Paulo": "Brasil Este 🇧🇷",
        "Europe/Madrid": "España 🇪🇸",
        "Europe/London": "Reino Unido 🇬🇧",
        "Europe/Paris": "Europa Central 🇪🇺",
        "Asia/Tokyo": "Japón 🇯🇵",
        "Asia/Shanghai": "China 🇨🇳",
        "Asia/Kolkata": "India 🇮🇳",
        "Australia/Sydney": "Australia Este 🇦🇺",
    }

    regions = []
    for z in zones:
        region = zone_to_region.get(z, z.replace("_", " ").replace("/", " → "))
        regions.append(region)

    return {
        "regiones_posibles": regions,
        "numero_zonas": len(zones),
        "precision": "Alta" if len(zones) == 1 else f"Media ({len(zones)} zonas posibles)",
    }


def compare_activity_pattern(zones: list, hora_vista_activo: str = None) -> dict:
    """
    Si tienes una hora en que viste al usuario activo (ej: última vez en WhatsApp),
    cruza esa hora con las zonas horarias para inferir dónde podría estar.

    hora_vista_activo: formato "HH:MM" en UTC
    """
    if not hora_vista_activo:
        return {"nota": "No se proporcionó hora de última actividad para cruzar"}

    try:
        h, m = map(int, hora_vista_activo.split(":"))
        now_utc = datetime.now(timezone.utc).replace(hour=h, minute=m)

        print(f"\n[*] Cruzando hora de actividad {hora_vista_activo} UTC con zonas horarias:")
        print(f"    {'─'*50}")

        candidates = []
        for tz_name in zones:
            tz = pytz.timezone(tz_name)
            local_time = now_utc.astimezone(tz)
            local_hour = local_time.hour

            # Horas más probables de actividad humana normal
            if 8 <= local_hour < 23:
                prob = "✅ Hora coherente con actividad normal"
            elif 6 <= local_hour < 8:
                prob = "⚠️  Hora muy temprana, poco probable"
            else:
                prob = "❌ Madrugada, muy improbable estar activo"

            candidates.append({
                "zona": tz_name,
                "hora_local": local_time.strftime("%H:%M"),
                "evaluacion": prob
            })
            print(f"    {tz_name:<35} → {local_time.strftime('%H:%M')} | {prob}")

        return {"candidatos": candidates}

    except Exception as e:
        return {"error": str(e)}


def run_timezone_analysis(phone: str, hora_activo: str = None, save: str = None):
    """Pipeline principal de análisis de zona horaria."""
    print(f"\n{'='*55}")
    print(f"  ANÁLISIS DE ZONA HORARIA: {phone}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"{'='*55}")

    zones = get_timezones(phone)
    if not zones:
        print("[!] No se pudieron obtener zonas horarias.")
        return

    print(f"\n[*] Zonas horarias del prefijo: {zones}")

    # Analizar cada zona
    analysis = []
    print(f"\n[*] Estado actual en cada zona horaria:")
    print(f"    {'─'*50}")
    for tz in zones:
        info = analyze_timezone(tz)
        analysis.append(info)
        print(f"\n    📍 {info['zona_horaria']}")
        print(f"       Hora allí:    {info.get('hora_actual_alli', 'N/A')}")
        print(f"       Día:          {info.get('dia_semana', 'N/A')}")
        print(f"       Período:      {info.get('periodo_del_dia', 'N/A')}")
        print(f"       Actividad:    {info.get('estimacion_actividad', 'N/A')}")

    # Inferencia de ubicación
    location_inference = infer_location_by_timezone(zones)
    print(f"\n[*] Inferencia de ubicación:")
    print(f"    {'─'*50}")
    for region in location_inference["regiones_posibles"]:
        print(f"    → {region}")
    print(f"    Precisión: {location_inference['precision']}")

    # Cruce con hora de actividad si se proporcionó
    activity_cross = {}
    if hora_activo:
        activity_cross = compare_activity_pattern(zones, hora_activo)

    # Reporte final
    report = {
        "numero": phone,
        "timestamp": datetime.now().isoformat(),
        "zonas_horarias": zones,
        "analisis_por_zona": analysis,
        "inferencia_ubicacion": location_inference,
        "cruce_actividad": activity_cross,
    }

    print(f"\n{'='*55}")
    print(f"  CONCLUSIÓN:")
    print(f"  El número tiene prefijo de: {', '.join(location_inference['regiones_posibles'])}")
    print(f"  Precisión de la estimación: {location_inference['precision']}")
    print(f"{'='*55}\n")

    if save:
        with open(save, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[+] Reporte guardado en: {save}")

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 timezone_inference.py <numero> [hora_activo_utc] [-o output.json]")
        print("  Ej básico:   python3 timezone_inference.py +573001234567")
        print("  Con cruce:   python3 timezone_inference.py +573001234567 14:30")
        print("  Con reporte: python3 timezone_inference.py +573001234567 14:30 -o report.json")
        sys.exit(1)

    phone = sys.argv[1]
    hora = sys.argv[2] if len(sys.argv) > 2 and ":" in sys.argv[2] else None
    output = None
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        output = sys.argv[idx + 1]

    run_timezone_analysis(phone, hora_activo=hora, save=output)
