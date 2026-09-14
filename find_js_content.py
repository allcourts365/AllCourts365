import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Look for ALL view_file responses containing athlete_calendar content
# They might show different ranges of the file
results = []
for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    content = data.get("content", "")
    if "athlete_calendar" in str(data) and len(content) > 5000 and ("function " in content or "{% for" in content):
        # Find HTML portions
        for keyword in ["renderMainCalendar", "openScheduleModal", "function selectSlot", "submitScheduleForm"]:
            if keyword in content:
                idx = content.find(keyword)
                results.append((step_index, keyword, content[max(0,idx-100):idx+500]))
                
for r in results[:10]:
    print(f"Step {r[0]}: found '{r[1]}'")
    print(r[2][:300])
    print("---")
