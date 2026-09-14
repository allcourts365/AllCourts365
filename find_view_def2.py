import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Search all tool calls content for "athlete_calendar" in views.py edits
for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index > 955:
        break
    if data.get("type") == "PLANNER_RESPONSE":
        for tool in data.get("tool_calls", []):
            args = tool.get("args", {})
            tf = args.get("TargetFile", "")
            if "views.py" in tf:
                rc = args.get("ReplacementContent", "")
                rcs = args.get("ReplacementChunks", [])
                for ch in rcs:
                    rcc = ch.get("ReplacementContent","")
                    if "athlete_calendar" in rcc:
                        print(f"Step {step_index}: chunk with athlete_calendar in views.py")
                        print(rcc[:500])
                        print("---")
                if "athlete_calendar" in rc:
                    print(f"Step {step_index}: replacement with athlete_calendar in views.py")
                    print(rc[:500])
