import json, re

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# At step 28, extract the full file content
# At step 34, there might be more content (lines 800+)
# Collect all unique lines from all view_file responses for athlete_calendar.html

all_file_lines = {}

for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index > 40:  # Only want original file content (before edits at step 39)
        break
    content = data.get("content", "")
    # Look for the numbered lines pattern: "NUMBER: CONTENT"
    if "{% extends" in content or "function renderMainCalendar" in content:
        # Extract numbered lines
        for match in re.finditer(r'(\d+): (.*?)(?=\r?\n\d+: |\Z)', content, re.DOTALL):
            line_num = int(match.group(1))
            line_content = match.group(2).replace("\r", "")
            if line_num not in all_file_lines:
                all_file_lines[line_num] = line_content

print(f"Found {len(all_file_lines)} unique lines")
if all_file_lines:
    max_line = max(all_file_lines.keys())
    min_line = min(all_file_lines.keys())
    print(f"Line range: {min_line} to {max_line}")
