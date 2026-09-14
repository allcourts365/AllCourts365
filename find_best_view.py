import json, re

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the LARGEST view_file response near step 951
# where athlete_calendar content is shown
best_step = 0
best_content = ""
best_start_line = 9999
best_end_line = 0

for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index > 960:
        break
    content = data.get("content", "")
    if "athlete_calendar.html" in content and len(content) > 20000:
        # Find line number range shown
        nums = re.findall(r'^(\d+): ', content, re.MULTILINE)
        if nums:
            start_n = int(nums[0])
            end_n = int(nums[-1])
            # Prefer content closer to step 951 that shows later parts of file
            if end_n > best_end_line:
                best_step = step_index
                best_content = content
                best_start_line = start_n
                best_end_line = end_n

print(f"Best view_file at step {best_step}: lines {best_start_line}-{best_end_line}, {len(best_content)} chars")

# Also try to find any step near 951 that shows a large portion
for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index < 900 or step_index > 960:
        continue
    content = data.get("content", "")
    if "athlete_calendar" in content and len(content) > 5000:
        nums = re.findall(r"'(\d+)': '", content)
        if not nums:
            nums = re.findall(r'^(\d+): ', content, re.MULTILINE)
        if nums:
            print(f"Step {step_index}: {len(content)} chars, lines {nums[0]}-{nums[-1]}")
