import json, re

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Check the current file for key features of 20:31 state
with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    html = f.read()

checks = [
    "filterDropdown", "toggleFilterDropdown", "btn-filter",
    "modal-delete-btn", "modal-save-btn-text",
    "editExistingSchedule", "openEmptyScheduleModal",
    "checkHoursAndAlert", "validateOpeningHours",
    "passado", "isPastDate",
    "month-view-container", "week-view-container",
    "standby_matches", "my_clubs",
    "clubs_hours_json", "all_matches_json",
    "Agendar", "Filtro",
    "AGENDADO", "AGUARDANDO",
    "submitDeleteSchedule", "submitScheduleForm",
]

print("=== CURRENT FILE MARKERS ===")
for c in checks:
    found = c in html
    status = "FOUND" if found else "MISSING"
    print(f"  [{status}] {c}")

print(f"\nTotal: {len(html)} chars, {html.count(chr(10))} lines")

bad = ["isPastMatch", "listToUse", "past_matches_json", "else {\\n                return; // User cancelled"]
print("\n=== BAD MARKERS (should NOT be present) ===")
for b in bad:
    print(f"  [{'FOUND BAD!' if b in html else 'OK'}] {b}")
