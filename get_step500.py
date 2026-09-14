import json, re

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Look at the replacement content at step 500 which edits views.py context dict
for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    if step_index != 500:
        continue
    if data.get("type") == "PLANNER_RESPONSE":
        for tool in data.get("tool_calls", []):
            args = tool.get("args", {})
            tf = args.get("TargetFile", "")
            if "views.py" in tf:
                tc = args.get("TargetContent","")
                rc = args.get("ReplacementContent","")
                print(f"Step 500 views.py edit:")
                print(f"TARGET ({len(tc)} chars):\n{tc[:2000]}")
                print(f"REPLACEMENT ({len(rc)} chars):\n{rc[:3000]}")
