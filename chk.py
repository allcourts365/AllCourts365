with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()
print(f"Lines: {content.count(chr(10))}, Chars: {len(content)}")
checks = [
    ("Event color agendado green", "#22c55e" in content or "rgba(34" in content or "agendado" in content),
    ("Event color red/orange", "rgba(239" in content or "rgba(220" in content or "rgb(239" in content),
    ("is_mine check in renderMainCalendar", "is_mine" in content),
    ("Agendar button", "Agendar" in content and "openEmptyScheduleModal" in content),
    ("Filtro button", "Filtro" in content and "filterDropdown" in content),
    ("editExistingSchedule", "editExistingSchedule" in content),
    ("isPast/passado validation", "isPast" in content or "passado" in content.lower()),
    ("checkHoursAndAlert", "checkHoursAndAlert" in content),
    ("standby list sidebar", "Jogos Aguardando" in content),
    ("my_clubs filter", "filter-cb-clube" in content),
    ("AGENDADO uppercase / toUpperCase", "AGENDADO" in content or "toUpperCase" in content),
    ("month-view-container", "month-view-container" in content),
    ("week-view-container", "week-view-container" in content),
    ("clubs_hours_json", "clubs_hours_json" in content),
    ("all_matches_json", "all_matches_json" in content),
    ("standby_matches", "standby_matches" in content),
    ("Todas as Quadras link", "clubs:list" in content or "Todas as Quadras" in content),
]
print()
for name, result in checks:
    print("  [OK] " + name if result else "  [MISSING] " + name)
