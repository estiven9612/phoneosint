#!/usr/bin/env python3
"""
PhoneOSINT - Herramienta educativa de análisis de números telefónicos
Solo para uso en entornos controlados y con autorización explícita.
"""

import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests
import json
import sys
import argparse
from datetime import datetime

BANNER = """
╔═══════════════════════════════════════════════════════╗
║           PhoneOSINT - Entorno Controlado             ║
║     Solo para uso educativo y autorizado              ║
╚═══════════════════════════════════════════════════════╝
"""

def parse_number(phone: str) -> phonenumbers.PhoneNumber | None:
    """Parsea y valida el número telefónico."""
    try:
        parsed = phonenumbers.parse(phone, None)
        if phonenumbers.is_valid_number(parsed):
            return parsed
        else:
            print(f"[!] Número inválido: {phone}")
            return None
    except phonenumbers.phonenumberutil.NumberParseException as e:
        print(f"[!] Error al parsear número: {e}")
        return None


def get_basic_info(parsed: phonenumbers.PhoneNumber) -> dict:
    """Obtiene información básica del número."""
    return {
        "numero_formateado": phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        ),
        "codigo_pais": parsed.country_code,
        "numero_nacional": parsed.national_number,
        "tipo": str(phonenumbers.number_type(parsed)),
        "valido": phonenumbers.is_valid_number(parsed),
        "posible": phonenumbers.is_possible_number(parsed),
    }


def get_geo_info(parsed: phonenumbers.PhoneNumber) -> dict:
    """Obtiene información geográfica aproximada."""
    region = geocoder.description_for_number(parsed, "es")
    zones = timezone.time_zones_for_number(parsed)
    return {
        "region_aproximada": region if region else "No disponible",
        "zonas_horarias": list(zones),
        "codigo_iso_pais": phonenumbers.region_code_for_number(parsed),
    }


def get_carrier_info(parsed: phonenumbers.PhoneNumber) -> dict:
    """Obtiene información del operador."""
    op = carrier.name_for_number(parsed, "es")
    return {
        "operador": op if op else "No disponible / Número fijo",
    }


def query_ip_api(phone_region: str) -> dict:
    """
    Consulta información pública de geolocalización del país/región.
    NOTA: Esto NO rastrea el dispositivo, solo consulta datos del país registrado.
    """
    try:
        # Solo consultamos info del país, no del dispositivo
        url = f"https://restcountries.com/v3.1/alpha/{phone_region}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()[0]
            capital = data.get("capital", ["N/A"])[0]
            region_world = data.get("region", "N/A")
            subregion = data.get("subregion", "N/A")
            population = data.get("population", "N/A")
            return {
                "pais": data.get("name", {}).get("common", "N/A"),
                "capital": capital,
                "region_mundo": region_world,
                "subregion": subregion,
                "poblacion": population,
            }
    except Exception:
        pass
    return {"pais": "No disponible"}


def print_report(number: str, results: dict):
    """Imprime el reporte formateado."""
    print(f"\n{'='*55}")
    print(f"  REPORTE: {number}")
    print(f"  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    sections = {
        "📋 Información Básica": results.get("basic", {}),
        "📍 Geolocalización Aproximada": results.get("geo", {}),
        "📡 Operador": results.get("carrier", {}),
        "🌍 Datos del País": results.get("country", {}),
    }

    for title, data in sections.items():
        print(f"\n  {title}")
        print(f"  {'-'*40}")
        for key, val in data.items():
            print(f"    {key:<25} {val}")

    print(f"\n{'='*55}")
    print("  ⚠️  Esta información es aproximada y de fuentes públicas.")
    print("  ⚠️  NO indica la ubicación real del dispositivo.")
    print(f"{'='*55}\n")


def save_report(number: str, results: dict, output_file: str):
    """Guarda el reporte en JSON."""
    report = {
        "numero": number,
        "timestamp": datetime.now().isoformat(),
        "resultados": results,
        "disclaimer": "Herramienta educativa. Uso solo en entornos controlados con autorización."
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[+] Reporte guardado en: {output_file}")


def analyze(number: str, save: str = None):
    """Pipeline principal de análisis."""
    print(BANNER)
    print(f"[*] Analizando: {number}")

    parsed = parse_number(number)
    if not parsed:
        sys.exit(1)

    results = {
        "basic": get_basic_info(parsed),
        "geo": get_geo_info(parsed),
        "carrier": get_carrier_info(parsed),
    }

    iso = results["geo"].get("codigo_iso_pais", "")
    if iso:
        results["country"] = query_ip_api(iso)

    print_report(number, results)

    if save:
        save_report(number, results, save)


def main():
    parser = argparse.ArgumentParser(
        description="PhoneOSINT - Análisis OSINT de números telefónicos (entorno controlado)"
    )
    parser.add_argument(
        "numero",
        help="Número telefónico en formato internacional (ej: +573001234567)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Guardar reporte en archivo JSON",
        default=None
    )
    args = parser.parse_args()
    analyze(args.numero, save=args.output)


if __name__ == "__main__":
    main()
