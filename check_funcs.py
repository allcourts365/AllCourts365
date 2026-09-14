with open("templates/athlete_calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

# Print the full editExistingSchedule and submitDeleteSchedule
for fname in ["function editExistingSchedule", "function submitDeleteSchedule"]:
    idx = content.find(fname)
    if idx >= 0:
        ln = content[:idx].count("\n") + 1
        # Find end of function by counting braces
        depth = 0
        end = idx
        for i, c in enumerate(content[idx:]):
            if c == "{": depth += 1
            elif c == "}": 
                depth -= 1
                if depth == 0:
                    end = idx + i + 1
                    break
        print(f"=== {fname} (line {ln}) ===")
        print(content[idx:end])
        print()
