#!/usr/bin/env python3
"""
Módulo HLR Lookup - Verifica operador actual y estado del número.
Usa APIs públicas/gratuitas. Solo para entornos controlados.

HLR = Home Location Register: base de datos de los operadores que
almacena info de suscriptores móviles activos.
"""

import requests
import json
import sys
import time
from datetime import datetime

# ----------------------------------------------------------------
# APIS GRATUITAS DISPONIBLES
# Puedes usar cualquiera de estas (algunas requieren registro free)
# ----------------------------------------------------------------
APIS = {
    "numverify": {
        "url": "http://apilayer.net/api/validate",
        "params_key": "access_key",
        "doc": "https://numverify.com/ - 100 req/mes gratis"
    },
    "abstract": {
        "url": "https://phonevalidation.abstractapi.com/v1/",
        "params_key": "api_key",
        "doc": "https://www.abstractapi.com/phone-validation-api - 250 req/mes gratis"
    }
}


def hlr_numverify(phone: str, api_key: str) -> dict:
    """
    Consulta Numverify API.
    Registro gratis en: https://numverify.com/
    Plan free: 100 consultas/mes
    """
    try:
        params = {
            "access_key": api_key,
            "number": phone,
            "format": 1
        }
        resp = requests.get(APIS["numverify"]["url"], params=params, timeout=10)
        data = resp.json()

        if data.get("valid"):
            return {
                "fuente": "Numverify",
                "valido": data.get("valid"),
                "numero": data.get("number"),
                "pais": data.get("country_name"),
                "codigo_pais": data.get("country_code"),
                "prefijo": data.get("country_prefix"),
                "operador_actual": data.get("carrier"),
                "tipo_linea": data.get("line_type"),  # mobile, landline, voip
                "location": data.get("location"),
            }
        else:
            return {"fuente": "Numverify", "error": data.get("error", {}).get("info", "No disponible")}

    except Exception as e:
        return {"fuente": "Numverify", "error": str(e)}


def hlr_abstract(phone: str, api_key: str) -> dict:
    """
    Consulta Abstract API Phone Validation.
    Registro gratis en: https://www.abstractapi.com/
    Plan free: 250 consultas/mes
    """
    try:
        params = {
            "api_key": api_key,
            "phone": phone
        }
        resp = requests.get(APIS["abstract"]["url"], params=params, timeout=10)
        data = resp.json()

        return {
            "fuente": "AbstractAPI",
            "valido": data.get("valid"),
            "numero": data.get("phone"),
            "formato_local": data.get("format", {}).get("local"),
            "formato_intl": data.get("format", {}).get("international"),
            "pais": data.get("country", {}).get("name"),
            "codigo_pais": data.get("country", {}).get("code"),
            "operador_actual": data.get("carrier"),
            "tipo_linea": data.get("type"),  # mobile, landline, voip, unknown
            "region": data.get("location"),
            "zona_horaria": data.get("timezone"),
        }

    except Exception as e:
        return {"fuente": "AbstractAPI", "error": str(e)}


def hlr_sin_api(phone: str) -> dict:
    """
    Análisis básico SIN necesidad de API key.
    Usa servicios públicos de validación de formato.
    """
    try:
        # Servicio público sin auth
        url = f"https://phonevalidation.abstractapi.com/v1/?api_key=demo&phone={phone}"
        # Como alternativa, usamos phonenumbers que es offline
        import phonenumbers
        from phonenumbers import carrier, geocoder, timezone

        parsed = phonenumbers.parse(phone, None)
        op = carrier.name_for_number(parsed, "es")
        region = geocoder.description_for_number(parsed, "es")
        zones = timezone.time_zones_for_number(parsed)
        line_type = phonenumbers.number_type(parsed)

        type_map = {
            0: "FIJO",
            1: "MOVIL",
            2: "MOVIL_O_FIJO",
            3: "TARIFA_ESPECIAL",
            4: "NUMEROS_ESPECIALES",
            5: "PAGER",
            6: "VoIP",
            7: "PERSONAL",
            8: "PREMIUM",
            9: "COMPARTIDO",
            10: "UAN",
            11: "VOICEMAIL",
            27: "DESCONOCIDO"
        }

        return {
            "fuente": "phonenumbers (offline)",
            "valido": phonenumbers.is_valid_number(parsed),
            "operador_registrado": op if op else "No disponible",
            "region": region if region else "No disponible",
            "tipo_linea": type_map.get(line_type, "DESCONOCIDO"),
            "zonas_horarias": list(zones),
            "nota": "Sin API key - datos del prefijo original, no del operador actual si fue portado"
        }

    except Exception as e:
        return {"fuente": "offline", "error": str(e)}


def run_hlr(phone: str, api: str = None, api_key: str = None) -> dict:
    """
    Ejecuta el HLR lookup con la fuente disponible.
    Si no hay API key, usa análisis offline.
    """
    print(f"\n[*] HLR Lookup: {phone}")
    print(f"    {'─'*45}")

    if api == "numverify" and api_key:
        result = hlr_numverify(phone, api_key)
    elif api == "abstract" and api_key:
        result = hlr_abstract(phone, api_key)
    else:
        print("    [!] Sin API key - usando análisis offline")
        result = hlr_sin_api(phone)

    # Imprimir resultados
    for key, val in result.items():
        if key != "fuente":
            print(f"    {key:<25} {val}")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 hlr_lookup.py <numero> [api] [api_key]")
        print("  Sin API:  python3 hlr_lookup.py +573001234567")
        print("  Con API:  python3 hlr_lookup.py +573001234567 numverify TU_API_KEY")
        sys.exit(1)

    phone = sys.argv[1]
    api = sys.argv[2] if len(sys.argv) > 2 else None
    key = sys.argv[3] if len(sys.argv) > 3 else None

    result = run_hlr(phone, api, key)
    print(f"\n[+] Listo.")
