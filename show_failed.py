import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Get failed edits 229-300 for athlete_calendar.html
for line in lines:
    data = json.loads(line)
    step = data.get("step_index", 0)
    if step < 220 or step > 310:
        continue
    if data.get("type") == "PLANNER_RESPONSE":
        for tool in data.get("tool_calls", []):
            args = tool.get("args", {})
            if "athlete_calendar" not in args.get("TargetFile",""):
                continue
            tc = args.get("TargetContent","").replace("\r\n","\n")
            rc = args.get("ReplacementContent","").replace("\r\n","\n")
            print(f"\n=== STEP {step} ===")
            print("TARGET:", repr(tc[:200]))
            print("REPLACEMENT:", rc[:500])
