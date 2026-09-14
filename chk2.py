with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find the event rendering part (evDiv className / colors)
idx = content.find("evDiv.className")
if idx >= 0:
    print("EVENT DIV CLASS SECTION:")
    print(content[max(0,idx-200):idx+600])
    print("---")

# Find event color styles
idx2 = content.find("rgba(239")
if idx2 >= 0:
    print("\nRED COLOR SECTION:")
    print(content[max(0,idx2-200):idx2+400])

idx3 = content.find("#22c55e")
if idx3 >= 0:
    print("\nGREEN COLOR SECTION:")
    print(content[max(0,idx3-200):idx3+400])
