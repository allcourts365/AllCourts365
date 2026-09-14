with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

# Check 1: Is there a click handler on events?
print("=== CLICK HANDLERS ON EVENTS ===")
import re
for match in re.finditer(r"(onclick|addEventListener.*click|evDiv\.onclick)", content):
    idx = match.start()
    ln = content[:idx].count("\n") + 1
    print(f"Line {ln}: {content[max(0,idx-50):idx+150].strip()}")
    print("---")

# Check 2: editExistingSchedule function
print("\n=== editExistingSchedule ===")
idx = content.find("function editExistingSchedule")
if idx >= 0:
    ln = content[:idx].count("\n") + 1
    print(f"Line {ln}:")
    print(content[idx:idx+600])
else:
    print("MISSING editExistingSchedule!")

# Check 3: modal delete button
print("\n=== DELETE BUTTON IN MODAL ===")
idx2 = content.find("modal-delete-btn")
if idx2 >= 0:
    ln2 = content[:idx2].count("\n") + 1
    print(f"Line {ln2}: {content[max(0,idx2-100):idx2+300]}")
else:
    print("MISSING modal-delete-btn!")

# Check 4: submitDeleteSchedule
print("\n=== submitDeleteSchedule ===")
idx3 = content.find("submitDeleteSchedule")
if idx3 >= 0:
    ln3 = content[:idx3].count("\n") + 1
    print(f"Line {ln3}: {content[idx3:idx3+400]}")
else:
    print("MISSING submitDeleteSchedule!")
