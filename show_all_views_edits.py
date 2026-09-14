import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Extract ALL replacement content from views.py edits up to 951
# to build a picture of the complete view
for target_step in [45, 129, 153, 183, 500, 503, 506, 512, 536, 563, 575, 605, 629, 692, 836, 863]:
    for line in lines:
        data = json.loads(line)
        if data.get("step_index") != target_step:
            continue
        if data.get("type") == "PLANNER_RESPONSE":
            for tool in data.get("tool_calls",[]):
                args = tool.get("args",{})
                if "views.py" not in args.get("TargetFile",""):
                    continue
                tc = args.get("TargetContent","")
                rc = args.get("ReplacementContent","")
                rcs = args.get("ReplacementChunks",[])
                print(f"\n=== STEP {target_step} [{tool['name']}] ===")
                if rcs:
                    for i, ch in enumerate(rcs):
                        print(f"  Chunk {i+1}: target={repr(ch.get('TargetContent','')[:80])}")
                        print(f"  Replacement: {ch.get('ReplacementContent','')[:400]}")
                else:
                    print(f"  Target: {repr(tc[:100])}")
                    print(f"  Replacement: {rc[:600]}")
