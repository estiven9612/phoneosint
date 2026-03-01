#!/usr/bin/env python3
"""
Tests unitarios para PhoneOSINT
Ejecutar: python3 -m pytest tests/ -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from phoneosint import parse_number, get_basic_info, get_geo_info, get_carrier_info


class TestParseNumber:
    def test_numero_valido_colombia(self):
        parsed = parse_number("+573001234567")
        assert parsed is not None

    def test_numero_valido_usa(self):
        parsed = parse_number("+12025551234")
        assert parsed is not None

    def test_numero_invalido(self):
        parsed = parse_number("12345")
        assert parsed is None

    def test_numero_sin_prefijo(self):
        parsed = parse_number("3001234567")
        assert parsed is None


class TestGeoInfo:
    def test_colombia(self):
        parsed = parse_number("+573001234567")
        if parsed:
            geo = get_geo_info(parsed)
            assert geo["codigo_iso_pais"] == "CO"

    def test_usa(self):
        parsed = parse_number("+12025551234")
        if parsed:
            geo = get_geo_info(parsed)
            assert geo["codigo_iso_pais"] == "US"


class TestBasicInfo:
    def test_tipo_movil(self):
        parsed = parse_number("+573001234567")
        if parsed:
            info = get_basic_info(parsed)
            assert info["valido"] is True
            assert info["codigo_pais"] == 57


if __name__ == "__main__":
    # Correr tests básicos sin pytest
    print("[*] Corriendo tests básicos...\n")

    tests = [
        ("+573001234567", True),
        ("+12025551234", True),
        ("+34911234567", True),
        ("12345", False),
        ("numero_invalido", False),
    ]

    for number, expected_valid in tests:
        parsed = parse_number(number)
        valid = parsed is not None
        status = "✓" if valid == expected_valid else "✗"
        print(f"  {status} {number} → {'válido' if valid else 'inválido'}")
        if valid and parsed:
            geo = get_geo_info(parsed)
            op = get_carrier_info(parsed)
            print(f"      País: {geo['codigo_iso_pais']} | Región: {geo['region_aproximada']} | Operador: {op['operador']}")

    print("\n[+] Tests completados.")
