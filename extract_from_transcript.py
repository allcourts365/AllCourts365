import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Look for tool responses (view_file output) that contain large content of athlete_calendar.html
largest = ""
largest_step = 0

for line in lines:
    data = json.loads(line)
    step_index = data.get("step_index", 0)
    content = data.get("content", "")
    if "athlete_calendar" in content and len(content) > len(largest) and "{% extends" in content:
        largest = content
        largest_step = step_index

print(f"Largest athlete_calendar content found at step {largest_step}: {len(largest)} chars")
if largest:
    # Try to extract the HTML content from the response
    start = largest.find("{% extends")
    if start >= 0:
        html_content = largest[start:start+100000]
        print(f"HTML starts at position {start}")
        print(f"First 500 chars: {html_content[:500]}")
        with open("templates/athlete_calendar.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Saved!")
