import re

filepath = 'templates/knockout_bracket_print.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace .round min-width
content = re.sub(r'(\.round\s*\{[^}]*min-width:\s*)250px', r'\g<1>180px', content)

# Replace .matchup-wrapper padding and gap
content = re.sub(r'padding:\s*0\.5rem\s*0;', r'padding: 0.25rem 0;', content)
content = re.sub(r'gap:\s*0\.2rem;', r'gap: 0;', content)

# Replace .team padding and font-size
content = re.sub(r'padding:\s*0\.5rem;', r'padding: 0.25rem 0.4rem;', content)
content = re.sub(r'font-size:\s*0\.85rem;', r'font-size: 0.75rem;', content)

# Replace .match-info-top font-size
content = re.sub(r'font-size:\s*0\.65rem;', r'font-size: 0.55rem;\n            margin-bottom: 2px;', content)

# Modify .bracket-container gap
content = re.sub(r'(\.bracket-container\s*\{[^}]*gap:\s*)2rem', r'\g<1>1.5rem', content)

# Make round-header slightly smaller padding
content = re.sub(r'(\.round-header\s*\{[^}]*padding:\s*)0\.5rem', r'\g<1>0.3rem', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("CSS adjusted for tighter bracket.")
