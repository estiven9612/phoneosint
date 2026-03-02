#!/usr/bin/env python3
"""
Módulo de geolocalización por Cell ID usando OpenCelliD.
Uso educativo con tu propio dispositivo.
"""

import requests
import json
import sys
from datetime import datetime

# ─── CONFIGURA TU API KEY AQUÍ ───────────────────────────
API_KEY = "TU_API_KEY_AQUI"
# ─────────────────────────────────────────────────────────

# Operadores Colombia
MNC_COLOMBIA = {
    "101": "Claro",
    "102": "Movistar",
    "103": "Tigo",
    "111": "ETB",
}

def get_cell_location(mcc: int, mnc: int, lac: int, cid: int) -> dict:
    """Consulta OpenCelliD para obtener ubicación de la torre."""
    url = "https://opencellid.org/cell/get"
    params = {
        "key": API_KEY,
        "mcc": mcc,
        "mnc": mnc,
        "lac": lac,
        "cellid": cid,
        "format": "json"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data.get("status") == "ok":
            lat = data.get("lat")
            lon = data.get("lon")
            rang = data.get("range")  # precisión en metros

            return {
                "status": "encontrado",
                "latitud": lat,
                "longitud": lon,
                "precision_metros": rang,
                "google_maps": f"https://maps.google.com/?q={lat},{lon}",
                "operador": MNC_COLOMBIA.get(str(mnc), "Desconocido"),
                "torre": f"LAC:{lac} CID:{cid}",
            }
        else:
            return {
                "status": "no encontrado",
                "error": data.get("error", "Torre no registrada en OpenCelliD")
            }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def print_report(result: dict):
    """Imprime el reporte de geolocalización."""
    print(f"\n{'='*55}")
    print(f"  GEOLOCALIZACIÓN POR CELL ID")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    for key, val in result.items():
        print(f"  {key:<25} {val}")

    print(f"\n  ⚠️  Precisión aproximada, no GPS exacto.")
    print(f"  ⚠️  Muestra la ubicación de la torre, no del dispositivo.")
    print(f"{'='*55}\n")


def run(mcc=732, mnc=101, lac=None, cid=None, save=None):
    """Pipeline principal."""
    if not lac or not cid:
        print("[!] Debes proporcionar LAC y CID")
        sys.exit(1)

    print(f"[*] Consultando torre: MCC={mcc} MNC={mnc} LAC={lac} CID={cid}")
    result = get_cell_location(mcc, mnc, lac, cid)
    print_report(result)

    if save:
        with open(save, "w") as f:
            json.dump(result, f, indent=2)
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
