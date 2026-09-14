import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Get ALL replacement content from views.py edits steps 500-870
# Apply them to the current reverted views.py
with open("core/views.py", "r", encoding="utf-8") as f:
    content = f.read().replace("\r\n", "\n")

print(f"Starting views.py: {len(content)} chars")

applied = 0
failed = []

for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index > 955:
        break
    if data.get("type") == "PLANNER_RESPONSE":
        for tool in data.get("tool_calls", []):
            args = tool.get("args", {})
            tf = args.get("TargetFile", "")
            if "views.py" not in tf or "core" not in tf:
                continue
            if tool["name"] == "replace_file_content":
                tc = args.get("TargetContent","").replace("\r\n","\n")
                rc = args.get("ReplacementContent","").replace("\r\n","\n")
                if tc and tc in content:
                    content = content.replace(tc, rc, 1)
                    applied += 1
                elif tc:
                    failed.append((step_index, tc[:50]))
            elif tool["name"] == "multi_replace_file_content":
                for chunk in args.get("ReplacementChunks",[]):
                    tc = chunk.get("TargetContent","").replace("\r\n","\n")
                    rc = chunk.get("ReplacementContent","").replace("\r\n","\n")
                    if tc and tc in content:
                        content = content.replace(tc, rc, 1)
                        applied += 1
                    elif tc:
                        failed.append((step_index, tc[:50]))

print(f"Applied: {applied}, Failed: {len(failed)}")
print(f"Has athlete_calendar view: {'def athlete_calendar' in content}")
print(f"Result: {len(content)} chars")

with open("core/views.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Saved views.py!")
if failed:
    print("\nFirst 5 failed:")
    for s, t in failed[:5]:
        print(f"  Step {s}: {repr(t)}")
