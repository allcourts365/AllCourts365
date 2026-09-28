import sys
import re

try:
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Update the Right Menu Mobile inside {% else %} (authenticated)
    start_tag = '{% if club_context %}'
    end_tag = '{% else %}'
    
    start_idx = content.find(start_tag, content.find('<div class="right-menu-mobile" id="rightMenuMobile">'))
    end_idx = content.find(end_tag, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        raise Exception("Menu bloco não encontrado no base.html")

    new_menu = """{% if department %}
                    <a href="{% url 'athlete_dashboard' %}?club={{ club_context.id }}"><i class="fas fa-table-tennis"></i> Painel do Atleta</a>
                    <a href="#" onclick="if(typeof openTab === 'function') { openTab('rankings'); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-calendar-alt"></i> Torneios Sazonais</a>
                    <a href="#" onclick="if(typeof openTab === 'function') { openTab('knockouts'); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-project-diagram"></i> Torneios Eliminatórios</a>
                    {% if department.rules_pdf %}
                    <a href="{{ department.rules_pdf.url }}" target="_blank"><i class="fas fa-file-pdf"></i> Regulamento</a>
                    {% endif %}
                    <a href="{% url 'clubs:news_list' club_context.id %}"><i class="fas fa-newspaper"></i> Notícias {{ club_context.name }}</a>
                    <a href="{% url 'clubs:detail' club_context.id %}"><i class="fas fa-arrow-left"></i> Voltar ao Clube</a>
                    {% elif club_context %}"""
                    
    # Only replace if not already there
    if "{% if department %}" not in content[start_idx:end_idx]:
        content = content[:start_idx] + new_menu + content[start_idx + len('{% if club_context %}'):]

    # Add mobile-only CSS to hide elements
    css_str = "<style>\n@media (max-width: 768px) {\n    .hide-on-mobile { display: none !important; }\n}\n</style>"
    if ".hide-on-mobile" not in content:
        head_end = content.find('</head>')
        content = content[:head_end] + css_str + "\n" + content[head_end:]

    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("base.html modificado.")

    # 2. Update department_detail.html
    with open('templates/department_detail.html', 'r', encoding='utf-8') as f:
        dept_content = f.read()

    # Hide Regulamento button
    btn_container = '<div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">'
    new_btn_container = '<div class="hide-on-mobile" style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">'
    dept_content = dept_content.replace(btn_container, new_btn_container)

    # Hide tabs
    tabs_container = '<div class="tabs-container" style="justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap;">'
    new_tabs_container = '<div class="tabs-container hide-on-mobile" style="justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap;">'
    dept_content = dept_content.replace(tabs_container, new_tabs_container)
    
    with open('templates/department_detail.html', 'w', encoding='utf-8') as f:
        f.write(dept_content)
        
    print("department_detail.html modificado.")

except Exception as e:
    print(e)
