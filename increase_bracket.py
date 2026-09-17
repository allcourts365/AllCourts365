import re

filepath = 'templates/knockout_bracket_print.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Increase sizes back slightly to fill more space but still fit
content = content.replace('min-width: 180px;', 'min-width: 220px;')
content = content.replace('padding: 0.25rem 0;', 'padding: 0.4rem 0;')
content = content.replace('gap: 0;', 'gap: 0.1rem;')
content = content.replace('padding: 0.25rem 0.4rem;', 'padding: 0.4rem 0.5rem;')
content = content.replace('font-size: 0.75rem;', 'font-size: 0.8rem;')
content = content.replace('font-size: 0.55rem;', 'font-size: 0.6rem;')
content = content.replace('gap: 1.5rem;', 'gap: 1.8rem;')
content = content.replace('padding: 0.3rem;', 'padding: 0.4rem;')

# Add vertical centering to the body or bracket wrapper? 
# In print, centering vertically can be tricky. Let's just wrap the bracket in a flex container that centers it vertically if we want.
# Actually, the user just noticed the bottom margin is bigger because the content is smaller. Increasing the content size should naturally fix this.
# Also, let's remove any default margin-top if any. The body has padding: 20px. 
# Print margin is set to 1cm in @page.

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Bracket size increased slightly.")
