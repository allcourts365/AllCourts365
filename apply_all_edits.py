import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

with open("templates/athlete_calendar_original.html", "r", encoding="utf-8") as f:
    content = f.read().replace("\r\n", "\n")

print(f"Starting: {len(content)} chars, {content.count(chr(10))} lines")

applied = 0
failed_targets = []

for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index < 39:
        continue
    if step_index > 951:
        break
    if data.get("type") == "PLANNER_RESPONSE":
        for tool in data.get("tool_calls", []):
            args = tool.get("args", {})
            target_file = args.get("TargetFile", "")
            if "athlete_calendar.html" not in target_file:
                continue
            if tool["name"] == "replace_file_content":
                tc = args.get("TargetContent", "").replace("\r\n", "\n")
                rc = args.get("ReplacementContent", "").replace("\r\n", "\n")
                if tc and tc in content:
                    content = content.replace(tc, rc, 1)
                    applied += 1
                elif tc:
                    failed_targets.append((step_index, tc[:60]))
            elif tool["name"] == "multi_replace_file_content":
                for chunk in args.get("ReplacementChunks", []):
                    tc = chunk.get("TargetContent", "").replace("\r\n", "\n")
                    rc = chunk.get("ReplacementContent", "").replace("\r\n", "\n")
                    if tc and tc in content:
                        content = content.replace(tc, rc, 1)
                        applied += 1
                    elif tc:
                        failed_targets.append((step_index, tc[:60]))

print(f"\nApplied: {applied}")
print(f"Failed: {len(failed_targets)}")
print(f"\nResult: {len(content)} chars, {content.count(chr(10))} lines")

# Write final result
with open("templates/athlete_calendar.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Saved to athlete_calendar.html!")
print("\nFailed targets (first 10):")
for step, tc in failed_targets[:10]:
    print(f"  Step {step}: {repr(tc)}")
