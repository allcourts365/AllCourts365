import json

transcript_path = r'C:\Users\ferna\.gemini\antigravity-ide\brain\4c798de9-4f4b-44ec-8696-0dc008c07811\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    data = json.loads(line)
    if data.get("type") != "USER_INPUT":
        continue
    content = data.get("content", "")
    step = data.get("step_index", 0)
    lower_content = content.lower()
    # Broader search for editing/clicking on calendar events
    keywords = ["clicar", "agendar", "jogo que ja esta", "editar", "excluir", "reagend", "bot", "botao", "btn", "delete", "trash", "lixeira"]
    if any(k in lower_content for k in keywords) and 380 <= step <= 960:
        print(f"Step {step} - {content[:300]}")
        print("---")
