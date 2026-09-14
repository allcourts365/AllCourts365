import json, re

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Collect from steps 28 AND 34 (both view_file responses)
all_file_lines = {}

for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index > 40:
        break
    content = data.get("content", "")
    if "{% extends" in content or "function renderMainCalendar" in content or "function selectSlot" in content:
        for match in re.finditer(r'(\d+): (.*?)(?=\r?\n\r?\n|\r?\n(\d+): )', content, re.DOTALL):
            line_num = int(match.group(1))
            line_content = match.group(2).replace("\r\n", "\n").replace("\r", "")
            if line_num not in all_file_lines:
                all_file_lines[line_num] = line_content

print(f"Found {len(all_file_lines)} unique lines")
max_line = max(all_file_lines.keys()) if all_file_lines else 0
min_line = min(all_file_lines.keys()) if all_file_lines else 0
print(f"Line range: {min_line} to {max_line}")

# Reconstruct file
result = []
for i in range(1, max_line + 1):
    if i in all_file_lines:
        result.append(all_file_lines[i])
    else:
        result.append("")  # placeholder for missing lines

with open("templates/athlete_calendar_original.html", "w", encoding="utf-8") as f:
    f.write("\n".join(result))
print("Saved athlete_calendar_original.html")
