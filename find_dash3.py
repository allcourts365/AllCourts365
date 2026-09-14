import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    raw = f.read()

# Search for "athlete_dashboard" anywhere in tool calls
lines = raw.split("\n")
for i, line in enumerate(lines):
    if not line.strip():
        continue
    try:
        data = json.loads(line)
    except:
        continue
    step = data.get("step_index", 0)
    if step > 960:
        break
    content_str = json.dumps(data)
    if "athlete_dashboard.html" in content_str and "TargetFile" in content_str:
        print(f"Step {step}: FOUND athlete_dashboard.html in tool call!")
        # print first 500 chars of content
        print(content_str[:500])
        print("---")
