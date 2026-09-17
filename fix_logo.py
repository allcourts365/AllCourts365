import re

files = [
    'templates/club_detail.html',
    'templates/club_list.html',
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # club_detail.html
    pattern_detail = r'\{% if club\.logo %\}\s*<img src="\{\{ club\.logo\.url \}\}" alt="\{\{ club\.name \}\}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">\s*\{% else %\}\s*<img src="\{% static \'bolinha\.png\' %\}" style="width: 60px; height: 60px; opacity: 0\.8;">\s*\{% endif %\}'
    
    replacement_detail = r'''{% if club.logo %}
                <img src="{{ club.logo.url }}" alt="{{ club.name }}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%; transform: scale(calc({{ club.logo_size|default:100 }} / 100)); transform-origin: center;">
            {% else %}
                <img src="{% static 'bolinha.png' %}" style="width: 60px; height: 60px; opacity: 0.8; transform: scale(calc({{ club.logo_size|default:100 }} / 100)); transform-origin: center;">
            {% endif %}'''
            
    # club_list.html
    pattern_list = r'\{% if club\.logo %\}\s*<img src="\{\{ club\.logo\.url \}\}" alt="\{\{ club\.name \}\}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">\s*\{% else %\}\s*<img src="\{% static \'bolinha\.png\' %\}" style="width: 100%; height: 100%; opacity: 0\.8;">\s*\{% endif %\}'
    
    replacement_list = r'''{% if club.logo %}
                            <img src="{{ club.logo.url }}" alt="{{ club.name }}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%; transform: scale(calc({{ club.logo_size|default:100 }} / 100)); transform-origin: center;">
                        {% else %}
                            <img src="{% static 'bolinha.png' %}" style="width: 100%; height: 100%; opacity: 0.8; transform: scale(calc({{ club.logo_size|default:100 }} / 100)); transform-origin: center;">
                        {% endif %}'''

    if filepath == 'templates/club_detail.html':
        content, c = re.subn(pattern_detail, replacement_detail, content)
        print(f"Replaced {c} in {filepath}")
    else:
        content, c = re.subn(pattern_list, replacement_list, content)
        print(f"Replaced {c} in {filepath}")
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
