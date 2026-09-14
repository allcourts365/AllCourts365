with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

# Check what closes the toolbar div and if there is a Filtro button
idx = content.find("Filtro")
if idx >= 0:
    print("Filtro found at:")
    print(content[max(0,idx-300):idx+300])
else:
    print("Filtro NOT FOUND in file!")
    
# Find where toolbar ends
idx2 = content.find("</div>\n\n    <div class=\"ol-body\"")
if idx2 >= 0:
    line = content[:idx2].count("\n") + 1
    print(f"\nToolbar ends near line {line}")
    print(content[max(0,idx2-500):idx2+100])
