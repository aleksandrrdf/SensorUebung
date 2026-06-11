"""
SensorPy – Messdaten analysieren
=================================
Dieses Modul enthält alle Funktionen zur Analyse von Umweltmessdaten.

Aufgabe: Implementiert jede Funktion so, dass sie der Beschreibung
im Docstring entspricht. Die Signatur (Name, Parameter, Rückgabetyp)
darf NICHT verändert werden.

Datenformat (eine Zeile aus messdaten.csv als dict):
    {
        "sensor_id":       "S01",
        "timestamp":       "2024-03-01 08:00",
        "temperatur":      19.2,
        "luftfeuchtigkeit": 52.1,
        "co2":             480.0
    }
"""

import csv
#Fabian

# ──────────────────────────────────────────────────────────────
# PERSON A
# ──────────────────────────────────────────────────────────────

def load_data(filename: str) -> list[dict]:
    try:
        data = []
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Konvertiere numerische Felder zu float
                row['temperatur'] = float(row['temperatur'])
                row['luftfeuchtigkeit'] = float(row['luftfeuchtigkeit'])
                row['co2'] = float(row['co2'])
                data.append(row)
        return data
    except Exception:
        return []


def calculate_average(values: list[float]) -> float:
    return round(sum(values) / len(values), 2)


def find_extremes(values: list[float]) -> tuple[float, float]:
    return (min(values), max(values))


def count_above_threshold(values: list[float], threshold: float) -> int:
    """Zählt, wie viele Werte in der Liste den Schwellenwert überschreiten.

    Args:
        values:    Liste mit float-Werten
        threshold: Schwellenwert (Werte > threshold werden gezählt)

    Returns:
        Anzahl der Werte, die strikt grösser als threshold sind.

    Beispiel:
        >>> count_above_threshold([19.2, 27.1, 24.7, 33.2, 21.4], 25.0)
        2
    """
    return sum(1 for value in values if value > threshold)


# ──────────────────────────────────────────────────────────────
# PERSON B
# ──────────────────────────────────────────────────────────────

def classify_value(value: float, limits: dict) -> str:
    """Klassifiziert einen Messwert anhand von Grenzwerten.

    Die limits-dict hat folgende Struktur:
        {
            "niedrig":  <obere Grenze für "niedrig">,
            "normal":   <obere Grenze für "normal">,
            "hoch":     <obere Grenze für "hoch">
            # alles darüber gilt als "kritisch"
        }

    Args:
        value:  Der zu klassifizierende Messwert
        limits: Dict mit den Grenzwerten (siehe oben)

    Returns:
        Einen der folgenden Strings: "niedrig", "normal", "hoch", "kritisch"

    Beispiel (Temperatur-Grenzen: niedrig<18, normal<26, hoch<32):
        >>> grenzen = {"niedrig": 18.0, "normal": 26.0, "hoch": 32.0}
        >>> classify_value(15.0, grenzen)
        'niedrig'
        >>> classify_value(22.0, grenzen)
        'normal'
        >>> classify_value(28.5, grenzen)
        'hoch'
        >>> classify_value(35.0, grenzen)
        'kritisch'
    """
    if value < limits["niedrig"]:
        return "niedrig"
    if value < limits["normal"]:
        return "normal"
    if value < limits["hoch"]:
        return "hoch"
    return "kritisch"


def filter_by_sensor(data: list[dict], sensor_id: str) -> list[dict]:
    """Filtert die Messdaten nach einer bestimmten Sensor-ID.

    Args:
        data:      Liste von Messdaten-dicts (Ausgabe von load_data)
        sensor_id: Sensor-ID, nach der gefiltert werden soll (z. B. "S01")

    Returns:
        Neue Liste, die nur Einträge mit der angegebenen sensor_id enthält.
        Leere Liste, wenn kein passender Eintrag gefunden wird.

    Beispiel:
        >>> daten = load_data("data/messdaten.csv")
        >>> s01 = filter_by_sensor(daten, "S01")
        >>> all(d["sensor_id"] == "S01" for d in s01)
        True
    """
    return [entry for entry in data if entry.get("sensor_id") == sensor_id]


def generate_report(data: list[dict]) -> str:
    """Erstellt einen Textbericht aus den Messdaten.

    Der Bericht enthält:
    - Gesamtanzahl der Messungen
    - Durchschnitt, Min und Max für Temperatur, Luftfeuchtigkeit und CO2
    - Anzahl der kritischen Temperaturmessungen (> 30 °C)
    - Liste aller vorhandenen Sensor-IDs

    Args:
        data: Liste von Messdaten-dicts (Ausgabe von load_data)

    Returns:
        Formatierter mehrzeiliger String.

    Beispiel-Output (gekürzt):
        ========== SensorPy Bericht ==========
        Messungen total:       36
        Sensoren:              S01, S02

        -- Temperatur (°C) --
        Durchschnitt:          22.48
        Min / Max:             15.9 / 33.2
        Kritische Werte (>30): 2

        -- Luftfeuchtigkeit (%) --
        ...
        ======================================
    """
    def format_value(value: float | None) -> str:
        if value is None:
            return "-"
        return f"{value:.2f}".rstrip("0").rstrip(".") or "0"

    def summarize(values: list[float | None]) -> tuple[str, str]:
        clean_values = [value for value in values if value is not None]
        if not clean_values:
            return "-", "-"

        average = calculate_average(clean_values)
        minimum, maximum = find_extremes(clean_values)
        return format_value(average), f"{format_value(minimum)} / {format_value(maximum)}"

    temperatures = [entry.get("temperatur") for entry in data if entry.get("temperatur") is not None]
    humidity = [entry.get("luftfeuchtigkeit") for entry in data if entry.get("luftfeuchtigkeit") is not None]
    co2 = [entry.get("co2") for entry in data if entry.get("co2") is not None]

    sensor_ids: list[str] = []
    for entry in data:
        sensor_id = entry.get("sensor_id")
        if sensor_id and sensor_id not in sensor_ids:
            sensor_ids.append(sensor_id)

    temp_avg, temp_range = summarize(temperatures)
    humidity_avg, humidity_range = summarize(humidity)
    co2_avg, co2_range = summarize(co2)

    lines = [
        "========== SensorPy Bericht ==========",
        f"Messungen total:       {len(data)}",
        f"Sensoren:              {', '.join(sensor_ids)}",
        "",
        "-- Temperatur (°C) --",
        f"Durchschnitt:          {temp_avg}",
        f"Min / Max:             {temp_range}",
        f"Kritische Werte (>30): {count_above_threshold(temperatures, 30.0)}",
        "",
        "-- Luftfeuchtigkeit (%) --",
        f"Durchschnitt:          {humidity_avg}",
        f"Min / Max:             {humidity_range}",
        "",
        "-- CO2 (ppm) --",
        f"Durchschnitt:          {co2_avg}",
        f"Min / Max:             {co2_range}",
        "=" * 37,
    ]
    return "\n".join(lines)

