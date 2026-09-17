import re

filepath = 'templates/athlete_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find `<div style="height: 100px; position: relative; background: linear-gradient`
# Replace with `<div style="width: 100%; aspect-ratio: 4 / 1; position: relative; background: linear-gradient`

content, c1 = re.subn(r'height: 100px; position: relative; background: linear-gradient', r'width: 100%; aspect-ratio: 4 / 1; position: relative; background: linear-gradient', content)
content, c2 = re.subn(r'height: 80px; position: relative; background: linear-gradient', r'width: 100%; aspect-ratio: 4 / 1; position: relative; background: linear-gradient', content)

print(f"Replaced {c1} instances of 100px and {c2} instances of 80px in {filepath}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
