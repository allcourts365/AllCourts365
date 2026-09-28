import sys
import re

try:
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Removendo a cagada do bloco errado
    bad_block = """{% if department %}
                    <a href="{% url 'athlete_dashboard' %}?club={{ club_context.id }}"><i class="fas fa-table-tennis"></i> Painel do Atleta</a>
                    <a href="#" onclick="if(typeof openTab === 'function') { openTab('rankings'); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-calendar-alt"></i> Torneios Sazonais</a>
                    <a href="#" onclick="if(typeof openTab === 'function') { openTab('knockouts'); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-project-diagram"></i> Torneios Eliminatórios</a>
                    {% if department.rules_pdf %}
                    <a href="{{ department.rules_pdf.url }}" target="_blank"><i class="fas fa-file-pdf"></i> Regulamento</a>
                    {% endif %}
                    <a href="{% url 'clubs:news_list' club_context.id %}"><i class="fas fa-newspaper"></i> Notícias {{ club_context.name }}</a>
                    <a href="{% url 'clubs:detail' club_context.id %}"><i class="fas fa-arrow-left"></i> Voltar ao Clube</a>
                    {% elif club_context %}"""
                    
    content = content.replace(bad_block, "{% if club_context %}")

    # 2. Inserindo no bloco certo (sob user.is_authenticated)
    target = "{% if club_context %}"
    
    # precisamos achar o bloco correto, é depois de:
    # <div class="user-name-label"...
    
    label_start = content.find('<div class="user-name-label"')
    target_idx = content.find(target, label_start)
    
    new_block = """{% if department %}
                    <a href="{% url 'athlete_dashboard' %}?club={{ club_context.id }}"><i class="fas fa-table-tennis"></i> Painel do Atleta</a>
                    <a href="#" onclick="if(typeof openTab === 'function') { openTab('rankings'); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-calendar-alt"></i> Torneios Sazonais</a>
                    <a href="#" onclick="if(typeof openTab === 'function') { openTab('knockouts'); document.getElementById('rightMenuMobile').classList.remove('open'); } return false;"><i class="fas fa-project-diagram"></i> Torneios Eliminatórios</a>
                    {% if department.rules_pdf %}
                    <a href="{{ department.rules_pdf.url }}" target="_blank"><i class="fas fa-file-pdf"></i> Regulamento</a>
                    {% endif %}
                    <a href="{% url 'clubs:news_list' club_context.id %}"><i class="fas fa-newspaper"></i> Notícias {{ club_context.name }}</a>
                    <a href="{% url 'clubs:detail' club_context.id %}"><i class="fas fa-arrow-left"></i> Voltar ao Clube</a>
                    {% elif club_context %}"""
                    
    content = content[:target_idx] + new_block + content[target_idx + len(target):]

    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Corrigido com sucesso!")

except Exception as e:
    print(e)
