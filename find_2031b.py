import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find USER_INPUT messages around 20:31 local time (which was 23:31 UTC)
# The session summary says step 951 was the 20:31 checkpoint
# Let me find user messages near that time
for line in lines:
    data = json.loads(line)
    if data.get("type") != "USER_INPUT":
        continue
    content = data.get("content", "")
    step = data.get("step_index", 0)
    # Look for timestamp 20:31 in the metadata
    if "20:31" in content or "23:31" in content:
        print(f"Step {step}: FOUND 20:31!")
        print(content[:500])
        print("===")
    # Also check step range 890-960
    if 890 <= step <= 960:
        print(f"Step {step}: {content[:300]}")
        print("---")
