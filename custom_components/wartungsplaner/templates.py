"""Predefined German household maintenance task templates."""

from __future__ import annotations

from .const import IntervalUnit, TaskCategory, TaskPriority

TASK_TEMPLATES: list[dict] = [
    # --- Heizung ---
    {
        "id": "heizung_wartung",
        "name": "Heizungsanlage warten lassen",
        "description": "Jährliche Wartung der Heizungsanlage durch Fachbetrieb (Brenner, Filter, Abgaswerte)",
        "category": TaskCategory.HEATING,
        "priority": TaskPriority.HIGH,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "heizung_entlueften",
        "name": "Heizkörper entlüften",
        "description": "Alle Heizkörper entlüften, um Luftblasen zu entfernen und gleichmäßige Wärmeverteilung sicherzustellen",
        "category": TaskCategory.HEATING,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "heizung_thermostate",
        "name": "Thermostatventile prüfen",
        "description": "Thermostatventile auf korrekte Funktion prüfen, Gängigkeit testen",
        "category": TaskCategory.HEATING,
        "priority": TaskPriority.LOW,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    # --- Sicherheit ---
    {
        "id": "rauchmelder_test",
        "name": "Rauchmelder testen",
        "description": "Alle Rauchmelder auf Funktion testen (Testknopf drücken) und Batterien prüfen",
        "category": TaskCategory.SAFETY,
        "priority": TaskPriority.CRITICAL,
        "interval_value": 3,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "rauchmelder_batterie",
        "name": "Rauchmelder-Batterien wechseln",
        "description": "Batterien aller Rauchmelder austauschen (auch bei 10-Jahres-Batterien Ablaufdatum prüfen)",
        "category": TaskCategory.SAFETY,
        "priority": TaskPriority.CRITICAL,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "feuerloescher",
        "name": "Feuerlöscher prüfen",
        "description": "Feuerlöscher auf Druck, Verfallsdatum und Zugänglichkeit prüfen",
        "category": TaskCategory.SAFETY,
        "priority": TaskPriority.HIGH,
        "interval_value": 2,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "erste_hilfe",
        "name": "Erste-Hilfe-Kasten prüfen",
        "description": "Inhalt des Erste-Hilfe-Kastens auf Vollständigkeit und Haltbarkeit prüfen",
        "category": TaskCategory.SAFETY,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    # --- Sanitär ---
    {
        "id": "wasserleitungen",
        "name": "Wasserleitungen auf Lecks prüfen",
        "description": "Sichtbare Wasserleitungen und Anschlüsse auf Undichtigkeiten kontrollieren",
        "category": TaskCategory.PLUMBING,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 6,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "silikonfugen",
        "name": "Silikonfugen im Bad prüfen",
        "description": "Silikonfugen in Bad und Küche auf Schimmel und Risse kontrollieren, bei Bedarf erneuern",
        "category": TaskCategory.PLUMBING,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "abfluesse",
        "name": "Abflüsse reinigen",
        "description": "Abflüsse in Bad und Küche reinigen, Siebe säubern, Siphon bei Bedarf durchspülen",
        "category": TaskCategory.PLUMBING,
        "priority": TaskPriority.LOW,
        "interval_value": 3,
        "interval_unit": IntervalUnit.MONTHS,
    },
    # --- Geräte ---
    {
        "id": "waschmaschine",
        "name": "Waschmaschine reinigen",
        "description": "Waschmaschine mit Maschinenreiniger oder 90°C-Leerwäsche reinigen, Flusensieb säubern, Dichtung trocknen",
        "category": TaskCategory.APPLIANCES,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 2,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "spuelmaschine",
        "name": "Spülmaschine reinigen",
        "description": "Spülmaschine mit Maschinenreiniger durchlaufen lassen, Sieb und Sprüharme reinigen",
        "category": TaskCategory.APPLIANCES,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 2,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "kuehlschrank",
        "name": "Kühlschrank abtauen und reinigen",
        "description": "Kühlschrank komplett ausräumen, abtauen (falls nötig), reinigen und Dichtungen prüfen",
        "category": TaskCategory.APPLIANCES,
        "priority": TaskPriority.LOW,
        "interval_value": 6,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "dunstabzug",
        "name": "Dunstabzugshaube reinigen",
        "description": "Filter der Dunstabzugshaube reinigen oder austauschen, Fettablagerungen entfernen",
        "category": TaskCategory.APPLIANCES,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 3,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "trockner_flusensieb",
        "name": "Trockner-Flusensieb reinigen",
        "description": "Flusensieb und Wärmetauscher des Trockners reinigen",
        "category": TaskCategory.APPLIANCES,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 1,
        "interval_unit": IntervalUnit.MONTHS,
    },
    # --- Außen ---
    {
        "id": "dachrinne",
        "name": "Dachrinne reinigen",
        "description": "Dachrinnen und Fallrohre von Laub und Schmutz befreien",
        "category": TaskCategory.EXTERIOR,
        "priority": TaskPriority.HIGH,
        "interval_value": 6,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "fassade",
        "name": "Fassade kontrollieren",
        "description": "Hausfassade auf Risse, Abplatzungen und Schimmelbefall kontrollieren",
        "category": TaskCategory.EXTERIOR,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "fenster_dichtungen",
        "name": "Fensterdichtungen prüfen",
        "description": "Fensterdichtungen auf Risse und Versprödung prüfen, bei Bedarf Dichtungen austauschen oder pflegen",
        "category": TaskCategory.EXTERIOR,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "rolllaeden",
        "name": "Rollläden warten",
        "description": "Rollläden auf Funktion prüfen, Führungsschienen reinigen und Mechanik schmieren",
        "category": TaskCategory.EXTERIOR,
        "priority": TaskPriority.LOW,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    # --- Innen ---
    {
        "id": "lueftungsanlage",
        "name": "Lüftungsfilter wechseln",
        "description": "Filter der kontrollierten Wohnraumlüftung wechseln, Lüftungskanäle bei Bedarf reinigen",
        "category": TaskCategory.INTERIOR,
        "priority": TaskPriority.HIGH,
        "interval_value": 6,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "tuerscharniere",
        "name": "Türscharniere ölen",
        "description": "Alle Türscharniere und Schlösser mit geeignetem Öl schmieren",
        "category": TaskCategory.INTERIOR,
        "priority": TaskPriority.LOW,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "wasserhahn_perlator",
        "name": "Perlatoren entkalken",
        "description": "Perlatoren (Strahlregler) an allen Wasserhähnen abschrauben und entkalken",
        "category": TaskCategory.INTERIOR,
        "priority": TaskPriority.LOW,
        "interval_value": 6,
        "interval_unit": IntervalUnit.MONTHS,
    },
    # --- Elektrik ---
    {
        "id": "fi_schalter",
        "name": "FI-Schutzschalter testen",
        "description": "Alle FI-Schutzschalter (RCD) im Sicherungskasten durch Drücken der Prüftaste testen",
        "category": TaskCategory.ELECTRICAL,
        "priority": TaskPriority.CRITICAL,
        "interval_value": 6,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "steckdosen",
        "name": "Steckdosen und Schalter prüfen",
        "description": "Alle Steckdosen und Schalter auf festen Sitz, Verfärbungen und Wackelkontakte prüfen",
        "category": TaskCategory.ELECTRICAL,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "blitzschutz",
        "name": "Blitzschutzanlage prüfen lassen",
        "description": "Blitzschutzanlage (falls vorhanden) durch Fachbetrieb prüfen lassen",
        "category": TaskCategory.ELECTRICAL,
        "priority": TaskPriority.HIGH,
        "interval_value": 4,
        "interval_unit": IntervalUnit.YEARS,
    },
    # --- Garten ---
    {
        "id": "garten_bewaesserung",
        "name": "Bewässerungsanlage winterfest machen",
        "description": "Bewässerungssystem entleeren und winterfest machen (vor dem ersten Frost)",
        "category": TaskCategory.GARDEN,
        "priority": TaskPriority.HIGH,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    {
        "id": "garten_hecke",
        "name": "Hecke schneiden",
        "description": "Hecken in Form schneiden (Achtung: Vogelschutzzeiten beachten, März-September nur Formschnitt)",
        "category": TaskCategory.GARDEN,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 6,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "garten_rasenmaehen",
        "name": "Rasenmäher warten",
        "description": "Rasenmäher-Messer schärfen, Ölstand prüfen, Luftfilter reinigen, Zündkerze prüfen",
        "category": TaskCategory.GARDEN,
        "priority": TaskPriority.MEDIUM,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
    # --- Reinigung ---
    {
        "id": "matratze",
        "name": "Matratze reinigen und wenden",
        "description": "Matratze absaugen, Flecken behandeln und wenden oder drehen",
        "category": TaskCategory.CLEANING,
        "priority": TaskPriority.LOW,
        "interval_value": 3,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "fenster_putzen",
        "name": "Fenster putzen",
        "description": "Alle Fenster (innen und außen) gründlich reinigen",
        "category": TaskCategory.CLEANING,
        "priority": TaskPriority.LOW,
        "interval_value": 3,
        "interval_unit": IntervalUnit.MONTHS,
    },
    {
        "id": "teppich_reinigung",
        "name": "Teppiche grundreinigen",
        "description": "Teppiche und Teppichböden mit Teppichreiniger oder professionell reinigen lassen",
        "category": TaskCategory.CLEANING,
        "priority": TaskPriority.LOW,
        "interval_value": 1,
        "interval_unit": IntervalUnit.YEARS,
    },
]


def get_templates() -> list[dict]:
    """Return all available task templates."""
    return [{**t, "builtin": True} for t in TASK_TEMPLATES]


def get_template_by_id(template_id: str) -> dict | None:
    """Return a specific template by its ID."""
    for template in TASK_TEMPLATES:
        if template["id"] == template_id:
            return template
    return None


def get_templates_by_category(category: str) -> list[dict]:
    """Return templates filtered by category."""
    return [t for t in TASK_TEMPLATES if t["category"] == category]
