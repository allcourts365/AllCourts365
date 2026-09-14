with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find all places where ev.start.startsWith is used
import re
idx = 0
while True:
    idx = content.find("ev.start.startsWith", idx)
    if idx < 0:
        break
    line_num = content[:idx].count("\n") + 1
    print(f"Line {line_num}: {content[max(0,idx-200):idx+300]}")
    print("---")
    idx += 1
