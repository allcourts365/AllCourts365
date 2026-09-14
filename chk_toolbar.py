with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

# find toolbar section
for i, line in enumerate(lines):
    if "ol-toolbar" in line:
        print(f"Line {i+1}: {line.rstrip()}")
        for j in range(i, min(i+20, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        break
