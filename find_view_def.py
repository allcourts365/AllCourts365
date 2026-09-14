import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the FULL athlete_calendar view from views.py
# Look at step 500-512 where the view was first built
for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index < 490 or step_index > 520:
        continue
    if data.get("type") == "PLANNER_RESPONSE":
        for tool in data.get("tool_calls", []):
            args = tool.get("args", {})
            tf = args.get("TargetFile", "")
            if "views.py" in tf:
                rc = args.get("ReplacementContent", "")
                tc = args.get("TargetContent", "")
                if "athlete_calendar" in rc or "athlete_calendar" in tc:
                    print(f"Step {step_index}: {tool['name']}")
                    print("TARGET:", tc[:200])
                    print("REPLACEMENT:", rc[:3000])
                    print("---")
