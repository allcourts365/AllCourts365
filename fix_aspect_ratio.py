import re

files = [
    'templates/club_detail.html',
    'templates/club_list.html',
    'templates/athlete_dashboard.html'
]

# Step 1: Revert cover to contain
for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'object-fit: cover;( opacity: [0-9.]+; transform: scale)'
    replacement = r'object-fit: contain;\1'
    
    content, c = re.subn(pattern, replacement, content)
    print(f"Reverted {c} covers to contain in {filepath}")
    
    # Step 2: Replace fixed heights with aspect-ratio: 4/1 on the cover container
    # In club_detail.html:
    # <div style="width: 100%; height: 200px; position: relative; background: linear-gradient...
    
    # In club_list.html:
    # <div style="width: 100%; height: 120px; position: relative; background: linear-gradient...
    
    # In athlete_dashboard.html:
    # <div style="width: 100%; height: 100px; position: relative; background: linear-gradient...
    # There's also some 120px in athlete_dashboard?
    
    content, c2 = re.subn(r'width: 100%; height: 200px; position: relative;', r'width: 100%; aspect-ratio: 4 / 1; position: relative;', content)
    content, c3 = re.subn(r'width: 100%; height: 120px; position: relative;', r'width: 100%; aspect-ratio: 4 / 1; position: relative;', content)
    content, c4 = re.subn(r'width: 100%; height: 100px; position: relative;', r'width: 100%; aspect-ratio: 4 / 1; position: relative;', content)
    content, c5 = re.subn(r'width: 100%; height: 150px; position: relative;', r'width: 100%; aspect-ratio: 4 / 1; position: relative;', content)
    
    print(f"Replaced {c2+c3+c4+c5} fixed heights with aspect-ratio in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
