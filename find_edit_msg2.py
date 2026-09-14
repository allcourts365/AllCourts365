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
    keywords = ["editar agendamento", "modo edicao", "modo de edicao", "clicar no evento", "clicar no jogo", 
                "excluir agendamento", "botao excluir", "reagendar", "clicando no jogo", "clicando no evento",
                "editar o agendamento", "ao clicar", "quando clicar no"]
    if any(k in lower_content for k in keywords) and step < 960:
        print(f"Step {step} ({data.get('content','')[:30].strip()}):")
        print(content[:600])
        print("===")
