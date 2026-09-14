import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find ALL edits to any dashboard-related template
for line in lines:
    data = json.loads(line)
    step = data.get("step_index", 0)
    if step > 960:
        break
    if data.get("type") == "PLANNER_RESPONSE":
        for tool in data.get("tool_calls", []):
            args = tool.get("args", {})
            tf = args.get("TargetFile", "")
            if "dashboard" in tf.lower() or "meus_jogos" in tf.lower():
                print(f"Step {step}: [{tool['name']}] {tf}")
                rc = args.get("ReplacementContent", "")
                if rc:
                    print(rc[:400])
