with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find('<div class="ol-toolbar">')
if idx >= 0:
    print(content[idx:idx+2000])
