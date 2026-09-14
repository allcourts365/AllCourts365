import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find ALL edits to athlete_dashboard.html
for line in lines:
    data = json.loads(line)
    step = data.get("step_index", 0)
    if step > 960:
        break
    if data.get("type") == "PLANNER_RESPONSE":
        for tool in data.get("tool_calls", []):
            args = tool.get("args", {})
            tf = args.get("TargetFile", "")
            if "athlete_dashboard" in tf and ".html" in tf:
                tc = args.get("TargetContent","").replace("\r\n","\n")
                rc = args.get("ReplacementContent","").replace("\r\n","\n")
                rcs = args.get("ReplacementChunks",[])
                print(f"\n=== STEP {step} [{tool['name']}] ===")
                if rcs:
                    for i,ch in enumerate(rcs):
                        print(f"Chunk {i+1} TARGET: {repr(ch.get('TargetContent','')[:150])}")
                        print(f"Chunk {i+1} REPLACEMENT: {ch.get('ReplacementContent','')[:600]}")
                else:
                    print(f"TARGET: {repr(tc[:200])}")
                    print(f"REPLACEMENT: {rc[:800]}")
