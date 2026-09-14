import json, sys

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for line in lines:
    data = json.loads(line)
    step = data.get("step_index", 0)
    if step < 670 or step > 700:
        continue
    content = data.get("content", "")
    if "implementation_plan" in content or "editar" in content.lower() or "excluir" in content.lower():
        out.append(f"Step {step} [{data.get('type')}]:\n{content[:3000]}\n===")

with open("plan_content.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("saved")
