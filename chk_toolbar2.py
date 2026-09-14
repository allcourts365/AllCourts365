with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()
    lines = f.readlines()

# Find the HTML toolbar div (not the CSS)
idx = content.find('<div class="ol-toolbar">')
if idx >= 0:
    line_num = content[:idx].count("\n") + 1
    print(f"Toolbar div at line {line_num}:")
    print(content[idx:idx+800])
