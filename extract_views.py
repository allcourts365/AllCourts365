import json, re

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    raw_lines = f.readlines()

# Get the full views.py content as shown at step 474 (grep output)
# Extract all "core\views.py:NNN:    content" lines
views_lines = {}
for line in raw_lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index != 474:
        continue
    content = data.get("content", "")
    # Extract lines like "core\views.py:NNN:    content"
    for match in re.finditer(r'core\\views\.py:(\d+):(.*?)(?=\r?\n(?:>?\s*core\\views\.py:|\Z))', content, re.DOTALL):
        line_num = int(match.group(1))
        line_content = match.group(2).strip()
        views_lines[line_num] = line_content
    break

print(f"Got {len(views_lines)} lines from views.py at step 474")
if views_lines:
    print(f"Range: {min(views_lines)} - {max(views_lines)}")
    # Show the athlete_calendar function
    for ln in sorted(views_lines.keys()):
        if 718 <= ln <= 845:
            print(f"{ln}: {views_lines[ln]}")
