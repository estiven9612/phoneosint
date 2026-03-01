# 📡 PhoneOSINT

Herramienta educativa de análisis OSINT para números telefónicos, diseñada para **entornos controlados y práctica en laboratorio**.

> ⚠️ **AVISO LEGAL**: Esta herramienta es exclusivamente para uso educativo, en entornos controlados y con autorización explícita de todas las partes involucradas. El uso sin autorización puede ser ilegal.

---

## 🗂️ Estructura del Repositorio

```
phoneosint/
├── src/
│   └── phoneosint.py        # Script principal
├── modules/
│   └── batch_analysis.py    # Análisis masivo de números
├── data/
│   └── numeros_prueba.txt   # Números de ejemplo para testing
├── docs/
│   └── (documentación adicional)
├── tests/
│   └── (tests unitarios)
├── requirements.txt
├── install.sh
└── README.md
```

---

## ⚙️ Instalación en Kali Linux

```bash
git clone https://github.com/tu-usuario/phoneosint.git
cd phoneosint
chmod +x install.sh
sudo ./install.sh
```

O manualmente:
```bash
pip3 install -r requirements.txt --break-system-packages
```

---

## 🚀 Uso

### Análisis de un número individual
```bash
python3 src/phoneosint.py +573001234567
```

### Guardar reporte en JSON
```bash
python3 src/phoneosint.py +573001234567 -o reporte.json
```

### Análisis masivo desde archivo
```bash
python3 modules/batch_analysis.py data/numeros_prueba.txt
python3 modules/batch_analysis.py data/numeros.csv output.json
```

---

## 📊 Qué información obtiene

| Dato | Fuente | ¿Rastrea el dispositivo? |
|------|--------|--------------------------|
| País registrado del número | Base de datos pública de prefijos | ❌ No |
| Región/ciudad aproximada | Base de datos `phonenumbers` | ❌ No |
| Operador telefónico | Base de datos pública | ❌ No |
| Zona horaria | Prefijo internacional | ❌ No |
| Tipo de línea (móvil/fijo) | Prefijo internacional | ❌ No |
| Datos del país | API pública de países | ❌ No |

> **Importante**: Esta herramienta **NO** rastrea la ubicación en tiempo real del dispositivo. Solo analiza metadata pública asociada al prefijo del número.

---

## 🧠 ¿Cómo funciona?

1. **Parseo del número**: Usa la librería `phonenumbers` (basada en la base de datos de Google libphonenumber).
2. **Geolocalización por prefijo**: Identifica país y región registrada según el código de área.
3. **Lookup del operador**: Consulta la base de datos de operadores asociados al prefijo.
4. **Datos del país**: Consulta la API pública `restcountries.com` para datos adicionales.

---

## 🔬 Limitaciones (importantes para el aprendizaje)

- Los números VoIP o reasignados pueden no reflejar su país real.
- La región es la del **registro del número**, no la ubicación actual del usuario.
- Los operadores pueden haber cambiado si el número fue portado.
- Ninguna técnica OSINT pública puede dar ubicación GPS en tiempo real sin acceso al operador o al dispositivo.

---

## 📚 Recursos para aprender más

- [libphonenumber (Google)](https://github.com/google/libphonenumber)
- [Python phonenumbers docs](https://pypi.org/project/phonenumbers/)
- [OSINT Framework](https://osintframework.com/)
- [Kali Linux Docs](https://www.kali.org/docs/)

---

## 📜 Licencia

MIT License - Solo para uso educativo y en entornos controlados con autorización.
