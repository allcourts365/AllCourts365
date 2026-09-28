import sys

try:
    with open('templates/athlete_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Vamos substituir o bloco mobile_menu_extra pelo default_mobile_menu no athlete_dashboard.html
    # Além disso, o usuário pediu o botão Sair da conta e Regulamento.
    
    old_block = """{% block mobile_menu_extra %}
<a href="#" onclick="if(typeof openTab === 'function') { openTab('meu-clube', document.querySelector('.tab-btn')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-link"></i> Meu(s) Clube(s) / Liga(s)</a>
<a href="#" onclick="if(typeof openTab === 'function') { openTab('meu-perfil', document.querySelector('.tab-btn:nth-child(2)')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-user-edit"></i> Meu Perfil</a>
<a href="{% url 'athlete_calendar' %}"><i class="fas fa-calendar-alt"></i> Calendário</a>
<a href="{% url 'athlete_stats' %}"><i class="fas fa-chart-line"></i> Estatísticas</a>
<a href="#" onclick="if(typeof openTab === 'function') { openTab('mensagens', document.querySelector('.tab-btn:nth-child(5)')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-envelope"></i> Mensagens {% if unread_messages_count %}<span style="background: red; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8rem; margin-left: 5px;">{{ unread_messages_count }}</span>{% endif %}</a>
{% endblock %}"""

    new_block = """{% block default_mobile_menu %}
<a href="#" onclick="if(typeof openTab === 'function') { openTab('meu-clube', document.querySelector('.tab-btn')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-link"></i> Meu(s) Clube(s) / Liga(s)</a>
<a href="#" onclick="if(typeof openTab === 'function') { openTab('meu-perfil', document.querySelector('.tab-btn:nth-child(2)')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-user-edit"></i> Meu Perfil</a>
<a href="{% url 'athlete_calendar' %}"><i class="fas fa-calendar-alt"></i> Calendário</a>
<a href="{% url 'athlete_stats' %}"><i class="fas fa-chart-line"></i> Estatísticas</a>
<a href="#" onclick="if(typeof openTab === 'function') { openTab('mensagens', document.querySelector('.tab-btn:nth-child(5)')); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-envelope"></i> Mensagens {% if unread_messages_count %}<span style="background: red; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8rem; margin-left: 5px;">{{ unread_messages_count }}</span>{% endif %}</a>
{% if linked_club and linked_club.rules_pdf %}
<a href="{{ linked_club.rules_pdf.url }}" target="_blank"><i class="fas fa-file-pdf"></i> Regulamento</a>
{% endif %}
<a href="{% url 'account_logout' %}"><i class="fas fa-sign-out-alt"></i> Sair da Conta</a>
{% endblock %}"""

    if old_block in content:
        content = content.replace(old_block, new_block)
        with open('templates/athlete_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Substituição feita no athlete_dashboard.html")
    else:
        print("Não achou o old_block!")
        
except Exception as e:
    print(e)
