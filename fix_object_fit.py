import re

files = [
    'templates/club_detail.html',
    'templates/club_list.html',
    'templates/athlete_dashboard.html'
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # We want to replace object-fit: contain with object-fit: cover in the lines that have card_image_size scaling
    # Or just replace object-fit: contain with object-fit: cover anywhere inside the header image logic.
    # To be safe, we'll look for `object-fit: contain; opacity: 0.5; transform: scale` and replace it
    
    # Wait, in athlete_dashboard it might be `opacity: 0.6;` or `0.4;` etc.
    # Let's use a regex that matches `object-fit: contain; opacity: \d\.\d; transform: scale`
    
    pattern = r'object-fit: contain;( opacity: [0-9.]+; transform: scale)'
    replacement = r'object-fit: cover;\1'
    
    new_content, count = re.subn(pattern, replacement, content)
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Replaced {count} instances in {filepath}")
    else:
        print(f"No replacements found in {filepath}")
