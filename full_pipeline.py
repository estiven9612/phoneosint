#!/usr/bin/env python3
"""
PhoneOSINT FULL - Pipeline completo de análisis.
Corre todos los módulos en secuencia y genera reporte unificado.
Solo para entornos controlados con autorización.
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Agregar paths
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from phoneosint import parse_number, get_basic_info, get_geo_info, get_carrier_info, query_ip_api
from hlr_lookup import run_hlr
from osint_cruzado import run_osint
from timezone_inference import run_timezone_analysis

BANNER = """
╔══════════════════════════════════════════════════════════╗
║          PhoneOSINT FULL - Pipeline Completo             ║
║    Nivel 1: Prefijo  →  Nivel 2: HLR  →  Nivel 3: OSINT ║
║              Solo para entornos controlados              ║
╚══════════════════════════════════════════════════════════╝
"""


def full_pipeline(phone: str, api: str = None, api_key: str = None,
                  hora_activo: str = None, save: str = None):
    """
    Ejecuta el pipeline completo:
    1. Análisis básico de prefijo
    2. HLR Lookup (operador actual)
    3. OSINT cruzado (fuentes públicas)
    4. Inferencia por zona horaria
    """
    print(BANNER)
    print(f"[*] Objetivo: {phone}")
    print(f"[*] Inicio:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    report = {
        "numero": phone,
        "timestamp": datetime.now().isoformat(),
        "niveles": {}
    }

    # ── NIVEL 1: Análisis básico ──────────────────────────────
    print("\n" + "━"*55)
    print("  NIVEL 1 — Análisis de Prefijo (offline)")
    print("━"*55)

    parsed = parse_number(phone)
    if not parsed:
        print("[!] Número inválido. Abortando.")
        sys.exit(1)

    basic = get_basic_info(parsed)
    geo = get_geo_info(parsed)
    op = get_carrier_info(parsed)
    iso = geo.get("codigo_iso_pais", "")
    country = query_ip_api(iso) if iso else {}

    for k, v in {**basic, **geo, **op, **country}.items():
        print(f"  {k:<28} {v}")

    report["niveles"]["nivel_1_prefijo"] = {
        "basic": basic, "geo": geo, "carrier": op, "country": country
    }

    # ── NIVEL 2: HLR Lookup ───────────────────────────────────
    print("\n" + "━"*55)
    print("  NIVEL 2 — HLR Lookup (operador actual)")
    print("━"*55)

    hlr_result = run_hlr(phone, api=api, api_key=api_key)
    report["niveles"]["nivel_2_hlr"] = hlr_result

    # ── NIVEL 3: OSINT Cruzado ────────────────────────────────
    print("\n" + "━"*55)
    print("  NIVEL 3 — OSINT Cruzado (fuentes públicas)")
    print("━"*55)

    osint_result = run_osint(phone)
    report["niveles"]["nivel_3_osint"] = osint_result

    # ── NIVEL 4: Zona Horaria ─────────────────────────────────
    print("\n" + "━"*55)
    print("  NIVEL 4 — Inferencia por Zona Horaria")
    print("━"*55)

    tz_result = run_timezone_analysis(phone, hora_activo=hora_activo)
    report["niveles"]["nivel_4_timezone"] = tz_result

    # ── RESUMEN FINAL ─────────────────────────────────────────
    print("\n" + "═"*55)
    print("  RESUMEN EJECUTIVO")
    print("═"*55)
    print(f"  Número analizado:     {phone}")
    print(f"  País del prefijo:     {geo.get('codigo_iso_pais', 'N/A')} - {country.get('pais', 'N/A')}")
    print(f"  Región aproximada:    {geo.get('region_aproximada', 'N/A')}")
    print(f"  Operador registrado:  {op.get('operador', 'N/A')}")
    print(f"  Tipo de línea:        {basic.get('tipo', 'N/A')}")

    zones = tz_result.get("zonas_horarias", []) if tz_result else []
    if zones:
        print(f"  Zonas horarias:       {', '.join(zones)}")

    print(f"\n  ⚠️  Recuerda: esta info es aproximada y de fuentes públicas.")
    print(f"  ⚠️  No indica la ubicación GPS real del dispositivo.")
    print("═"*55)

    # Guardar reporte
    if save:
        with open(save, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[+] Reporte completo guardado en: {save}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="PhoneOSINT FULL - Pipeline completo de análisis"
    )
    parser.add_argument("numero", help="Número en formato internacional (ej: +573001234567)")
    parser.add_argument("--api", choices=["numverify", "abstract"], help="API para HLR lookup")
    parser.add_argument("--api-key", help="API key para HLR lookup")
    parser.add_argument("--hora-activo", help="Última hora vista activo en UTC (HH:MM) para cruce de zona horaria")
    parser.add_argument("-o", "--output", help="Guardar reporte JSON", default=None)

    args = parser.parse_args()

    full_pipeline(
        phone=args.numero,
        api=args.api,
        api_key=args.api_key,
        hora_activo=args.hora_activo,
        save=args.output
    )


if __name__ == "__main__":
    main()
