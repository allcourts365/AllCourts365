import re

filepath = 'templates/knockout_bracket_print.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Apply intermediate sizes
content = content.replace('min-width: 220px;', 'min-width: 200px;')
content = content.replace('padding: 0.4rem 0;', 'padding: 0.3rem 0;')
content = content.replace('gap: 0.1rem;', 'gap: 0;')
content = content.replace('padding: 0.4rem 0.5rem;', 'padding: 0.3rem 0.4rem;')
content = content.replace('font-size: 0.8rem;', 'font-size: 0.78rem;')
content = content.replace('font-size: 0.6rem;', 'font-size: 0.58rem;')
content = content.replace('gap: 1.8rem;', 'gap: 1.6rem;')
content = content.replace('padding: 0.4rem;', 'padding: 0.35rem;')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Bracket size adjusted to intermediate sweet spot.")
