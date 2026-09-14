with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find the full color assignment block before evDiv
idx = content.find("evDiv.className")
if idx >= 0:
    print(content[max(0,idx-800):idx+100])
