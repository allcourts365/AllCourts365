with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

# Show the event div creation block (day view) - no onclick?
idx = content.find("evDiv.className = `ol-event")
if idx >= 0:
    ln = content[:idx].count("\n") + 1
    print(f"Day view evDiv at line {ln}:")
    print(content[max(0,idx-50):idx+500])

print("\n\n")

# Check submitDeleteSchedule
idx2 = content.find("function submitDeleteSchedule")
if idx2 >= 0:
    ln2 = content[:idx2].count("\n") + 1
    print(f"submitDeleteSchedule at line {ln2}:")
    print(content[idx2:idx2+500])
else:
    print("MISSING submitDeleteSchedule!")
