#!/usr/bin/env python3
"""
Módulo de geolocalización por Cell ID usando UnwiredLabs.
100 consultas/día gratis. Solo para uso educativo con tu propio dispositivo.
Registro gratis en: https://unwiredlabs.com
"""

import requests
import json
import sys
from datetime import datetime

# ─── CONFIGURA TU TOKEN AQUÍ ─────────────────────────────
TOKEN = "TU_TOKEN_AQUI"
# ─────────────────────────────────────────────────────────

# Operadores Colombia
MNC_COLOMBIA = {
    "101": "Claro",
    "102": "Movistar",
    "103": "Tigo",
    "111": "ETB",
}


def get_cell_location_unwired(mcc: int, mnc: int, lac: int, cid: int) -> dict:
    url = "https://us1.unwiredlabs.com/v2/process.php"
    payload = {
        "token": TOKEN,
        "radio": "gsm",
        "mcc": mcc,
        "mnc": mnc,
        "cells": [{"lac": lac, "cid": cid}],
        "address": 1
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()

        if data.get("status") == "ok":
            lat = data.get("lat")
            lon = data.get("lon")
            accuracy = data.get("accuracy")
            address = data.get("address", "No disponible")

            return {
                "status": "encontrado",
                "latitud": lat,
                "longitud": lon,
                "precision_metros": accuracy,
                "direccion_aproximada": address,
                "google_maps": f"https://maps.google.com/?q={lat},{lon}",
                "operador": MNC_COLOMBIA.get(str(mnc), "Desconocido"),
                "torre": f"LAC:{lac} CID:{cid}",
                "balance": data.get("balance", "N/A")
            }
        else:
            return {
                "status": "no encontrado",
                "error": data.get("message", "Torre no registrada")
            }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def print_report(result: dict):
    print(f"\n{'='*55}")
    print(f"  GEOLOCALIZACIÓN POR CELL ID - UnwiredLabs")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")
    for key, val in result.items():
        print(f"  {key:<25} {val}")
    print(f"\n  ⚠️  Precisión aproximada, no GPS exacto.")
    print(f"  ⚠️  Muestra ubicación de la torre, no del dispositivo.")
    print(f"{'='*55}\n")


def run(mcc=732, mnc=101, lac=None, cid=None, save=None):
    if not lac or not cid:
        print("[!] Debes proporcionar LAC y CID")
        sys.exit(1)

    print(f"[*] Consultando torre: MCC={mcc} MNC={mnc} LAC={lac} CID={cid}")
    result = get_cell_location_unwired(mcc, mnc, lac, cid)
    print_report(result)

    if save:
        with open(save, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[+] Guardado en: {save}")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcc", type=int, default=732)
    parser.add_argument("--mnc", type=int, default=101)
    parser.add_argument("--lac", type=int, required=True)
    parser.add_argument("--cid", type=int, required=True)
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args()
    run(mcc=args.mcc, mnc=args.mnc, lac=args.lac, cid=args.cid, save=args.output)
