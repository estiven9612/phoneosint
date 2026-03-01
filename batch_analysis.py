#!/usr/bin/env python3
"""
Módulo de análisis masivo - analiza múltiples números desde archivo.
Uso educativo en entorno controlado.
"""

import csv
import json
import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from phoneosint import parse_number, get_basic_info, get_geo_info, get_carrier_info


def analyze_batch(input_file: str, output_file: str = "batch_report.json"):
    """Analiza múltiples números desde un archivo .txt o .csv"""
    numbers = []

    path = Path(input_file)
    if not path.exists():
        print(f"[!] Archivo no encontrado: {input_file}")
        sys.exit(1)

    # Leer números
    if path.suffix == ".csv":
        with open(path, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    numbers.append(row[0].strip())
    else:
        with open(path) as f:
            numbers = [line.strip() for line in f if line.strip()]

    print(f"[*] Procesando {len(numbers)} números...")

    results = []
    for num in numbers:
        parsed = parse_number(num)
        if parsed:
            entry = {
                "numero": num,
                "basic": get_basic_info(parsed),
                "geo": get_geo_info(parsed),
                "carrier": get_carrier_info(parsed),
            }
            results.append(entry)
            print(f"  [+] {num} → {entry['geo']['region_aproximada']} | {entry['carrier']['operador']}")
        else:
            print(f"  [-] {num} → inválido")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Reporte batch guardado en: {output_file}")
    print(f"[+] Números procesados: {len(results)}/{len(numbers)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 batch_analysis.py <archivo.txt|archivo.csv> [output.json]")
        sys.exit(1)
    
    input_f = sys.argv[1]
    output_f = sys.argv[2] if len(sys.argv) > 2 else "batch_report.json"
    analyze_batch(input_f, output_f)
