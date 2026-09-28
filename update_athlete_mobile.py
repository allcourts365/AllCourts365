import sys

try:
    with open('templates/athlete_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Adicionar class="hide-on-mobile" no wrapper dos botões (Regulamento e Sair)
    target1 = '<div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">'
    replacement1 = '<div class="hide-on-mobile" style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">'
    content = content.replace(target1, replacement1)

    # 2. Adicionar class="hide-on-mobile" no tabs-container
    target2 = '<div class="tabs-container">'
    replacement2 = '<div class="tabs-container hide-on-mobile">'
    content = content.replace(target2, replacement2)

    # 3. Inserir o bloco mobile_menu_extra logo após o block content
    menu_extra = """
{% block mobile_menu_extra %}
<a href="#" onclick="if(typeof openTab === 'function') { openTab('meu-clube', document.querySelector('.tab-btn')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-link"></i> Meu(s) Clube(s) / Liga(s)</a>
<a href="#" onclick="if(typeof openTab === 'function') { openTab('meu-perfil', document.querySelector('.tab-btn:nth-child(2)')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-user-edit"></i> Meu Perfil</a>
<a href="{% url 'athlete_calendar' %}"><i class="fas fa-calendar-alt"></i> Calendário</a>
<a href="{% url 'athlete_stats' %}"><i class="fas fa-chart-line"></i> Estatísticas</a>
<a href="#" onclick="if(typeof openTab === 'function') { openTab('mensagens', document.querySelector('.tab-btn:nth-child(5)')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-envelope"></i> Mensagens {% if unread_messages_count %}<span style="background: red; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8rem; margin-left: 5px;">{{ unread_messages_count }}</span>{% endif %}</a>
{% endblock %}
"""
    
    if "{% block mobile_menu_extra %}" not in content:
        content = content.replace('{% block content %}', '{% block content %}' + menu_extra)

    with open('templates/athlete_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Modificações do athlete_dashboard.html feitas com sucesso!")

except Exception as e:
    print(e)
