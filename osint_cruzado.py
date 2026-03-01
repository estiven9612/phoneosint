#!/usr/bin/env python3
"""
Módulo OSINT Cruzado - Busca el número en fuentes públicas.
Combina múltiples fuentes para construir un perfil aproximado.
Solo para entornos controlados con autorización.
"""

import requests
import json
import sys
import time
import urllib.parse
from datetime import datetime


def google_dork(phone: str) -> dict:
    """
    Genera Google Dorks para buscar el número en fuentes públicas.
    NOTA: Los dorks se generan para que el usuario los ejecute manualmente
    en el navegador, no se hace scraping directo de Google.
    """
    # Limpiar número para búsqueda
    clean = phone.replace("+", "").replace("-", "").replace(" ", "")
    formatted = phone  # formato original

    dorks = [
        f'"{formatted}"',
        f'"{formatted}" site:linkedin.com',
        f'"{formatted}" site:facebook.com',
        f'"{formatted}" site:twitter.com OR site:x.com',
        f'"{clean}" filetype:pdf',
        f'"{formatted}" inurl:contact OR inurl:contacto',
        f'"{formatted}" whatsapp',
        f'"{formatted}" telegram',
        f'"{formatted}" OLX OR mercadolibre OR clasificados',
    ]

    print("\n[*] Google Dorks generados para búsqueda manual:")
    print(f"    {'─'*50}")
    for i, dork in enumerate(dorks, 1):
        encoded = urllib.parse.quote(dork)
        url = f"https://www.google.com/search?q={encoded}"
        print(f"    [{i}] {dork}")
        print(f"        → {url}\n")

    return {"dorks": dorks, "total": len(dorks)}


def check_whatsapp_hints(phone: str) -> dict:
    """
    Genera URL de WhatsApp Click-to-Chat para verificar si el número
    tiene WhatsApp activo. El usuario debe abrirla manualmente.
    """
    clean = phone.replace("+", "").replace("-", "").replace(" ", "")

    wa_url = f"https://wa.me/{clean}"
    wa_api = f"https://api.whatsapp.com/send?phone={clean}"

    print("\n[*] Verificación WhatsApp (abrir manualmente):")
    print(f"    {'─'*50}")
    print(f"    Click-to-Chat: {wa_url}")
    print(f"    API URL:       {wa_api}")
    print(f"    [!] Si carga el chat → número activo en WhatsApp")
    print(f"    [!] Si da error → no tiene WhatsApp o número inválido")

    return {
        "wa_url": wa_url,
        "wa_api_url": wa_api,
        "instruccion": "Abrir manualmente en navegador para verificar"
    }


def check_telegram(phone: str) -> dict:
    """
    Intenta buscar el número en Telegram vía fragmento público.
    """
    clean = phone.replace("+", "").replace(" ", "")

    print("\n[*] Verificación Telegram:")
    print(f"    {'─'*50}")
    print(f"    [!] Buscar manualmente en Telegram app: '{phone}'")
    print(f"    [!] O usar: https://t.me/{clean} (si tiene username vinculado)")

    return {
        "instruccion": f"Buscar '{phone}' en Telegram app",
        "nota": "Si aparece perfil → número registrado en Telegram"
    }


def search_leaks(phone: str) -> dict:
    """
    Verifica si el número aparece en bases de datos de filtraciones conocidas.
    Usa APIs públicas de HIBP (Have I Been Pwned) y similares.
    """
    results = {}

    print("\n[*] Búsqueda en bases de datos de filtraciones:")
    print(f"    {'─'*50}")

    # Intel X / IntelligenceX (tiene buscador público)
    clean = phone.replace("+", "").replace(" ", "")
    intelx_url = f"https://intelx.io/?s={urllib.parse.quote(phone)}"
    print(f"    IntelligenceX: {intelx_url}")

    # Dehashed (requiere cuenta)
    dehashed_url = f"https://dehashed.com/search?query={urllib.parse.quote(phone)}"
    print(f"    Dehashed:      {dehashed_url}")

    # Leak-Lookup
    leaklookup_url = f"https://leak-lookup.com/search"
    print(f"    Leak-Lookup:   {leaklookup_url}")

    print(f"    [!] Abrir manualmente para verificar si el número está en filtraciones")

    results = {
        "intelx": intelx_url,
        "dehashed": dehashed_url,
        "leaklookup": leaklookup_url,
    }
    return results


def truecaller_manual(phone: str) -> dict:
    """
    Genera el enlace de búsqueda manual en Truecaller.
    (No tiene API pública gratuita sin registro)
    """
    clean = phone.replace("+", "")
    url = f"https://www.truecaller.com/search/co/{clean}"

    print("\n[*] Truecaller (nombre registrado por usuarios):")
    print(f"    {'─'*50}")
    print(f"    URL: {url}")
    print(f"    [!] Abrir en navegador para ver nombre registrado")

    return {"url": url, "nota": "Puede mostrar nombre real si está registrado"}


def generate_report(phone: str, results: dict) -> dict:
    """Genera reporte consolidado del OSINT cruzado."""
    report = {
        "numero": phone,
        "timestamp": datetime.now().isoformat(),
        "fuentes_consultadas": list(results.keys()),
        "resultados": results,
        "siguiente_paso": [
            "1. Ejecutar los Google Dorks en el navegador",
            "2. Verificar WhatsApp con el link generado",
            "3. Buscar en Truecaller",
            "4. Revisar filtraciones en IntelligenceX",
            "5. Cruzar toda la info con el módulo de zona horaria"
        ]
    }
    return report


def run_osint(phone: str, save: str = None):
    """Pipeline principal de OSINT cruzado."""
    print(f"\n{'='*55}")
    print(f"  OSINT CRUZADO: {phone}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    results = {}
    results["google_dorks"] = google_dork(phone)
    results["whatsapp"] = check_whatsapp_hints(phone)
    results["telegram"] = check_telegram(phone)
    results["truecaller"] = truecaller_manual(phone)
    results["filtraciones"] = search_leaks(phone)

    report = generate_report(phone, results)

    print(f"\n{'='*55}")
    print(f"  SIGUIENTES PASOS RECOMENDADOS:")
    print(f"{'='*55}")
    for paso in report["siguiente_paso"]:
        print(f"  {paso}")

    if save:
        with open(save, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[+] Reporte guardado en: {save}")

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 osint_cruzado.py <numero> [-o output.json]")
        print("  Ej: python3 osint_cruzado.py +573001234567")
        sys.exit(1)

    phone = sys.argv[1]
    output = None
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        output = sys.argv[idx + 1]

    run_osint(phone, save=output)
