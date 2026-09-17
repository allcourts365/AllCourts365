import re

filepath = 'templates/athlete_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(<div style="[^"]*position: relative;[^>]*>)\s*\{% if (.*?)\.card_image %\}\s*<img src="\{\{ \2\.card_image\.url \}\}" style="width: 100%; height: 100%; object-fit: cover; opacity: (.*?);">\s*\{% elif \2\.background_image %\}\s*<img src="\{\{ \2\.background_image\.url \}\}" style="width: 100%; height: 100%; object-fit: cover; opacity: \3;">\s*\{% endif %\}'

replacement = r'''\1
        <div style="width: 100%; height: 100%; overflow: hidden; position: absolute; top: 0; left: 0;">
            {% if \2.card_image %}
                <img src="{{ \2.card_image.url }}" style="width: 100%; height: 100%; object-fit: contain; opacity: \3; transform: scale(calc({{ \2.card_image_size|default:100 }} / 100)); transform-origin: center;">
            {% elif \2.background_image %}
                <img src="{{ \2.background_image.url }}" style="width: 100%; height: 100%; object-fit: contain; opacity: \3; transform: scale(calc({{ \2.card_image_size|default:100 }} / 100)); transform-origin: center;">
            {% endif %}
        </div>'''

new_content, count = re.subn(pattern, replacement, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Replaced {count} occurrences in {filepath}")
