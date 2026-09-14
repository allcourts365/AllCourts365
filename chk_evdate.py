with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find the day view event rendering section
idx = content.find("const evDate = new Date(ev.start)")
while idx >= 0:
    section = content[max(0,idx-100):idx+800]
    line_num = content[:idx].count("\n") + 1
    print(f"\n--- Found at line {line_num} ---")
    print(section)
    print("...")
    idx = content.find("const evDate = new Date(ev.start)", idx+1)
