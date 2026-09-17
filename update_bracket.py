import re

with open('templates/knockout_bracket.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the CSS related to tabs
content = re.sub(r'\.tabs-container {.*?\.tab-content\.active {\s*display: block;\s*}', '', content, flags=re.DOTALL)
content = re.sub(r'\.info-card {.*?\s*\}\s*', '', content, flags=re.DOTALL)

# Let's just remove the HTML sections.
# Find the bracket content
bracket_match = re.search(r'<div id="tab-chaves" class="tab-content">\s*(.*?)\s*</div>\s*<!-- Tab: Programação -->', content, flags=re.DOTALL)
if bracket_match:
    bracket_content = bracket_match.group(1)
    
    # We want to replace everything from <!-- Tabs --> to the end of the block content with just the bracket_content.
    new_html = f'''
<div style="margin-top: 2rem;">
    {bracket_content}
</div>
'''
    content = re.sub(r'<!-- Tabs -->.*?<script>.*?</script>', new_html, content, flags=re.DOTALL)

with open('templates/knockout_bracket.html', 'w', encoding='utf-8') as f:
    f.write(content)
