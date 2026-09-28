import sys

try:
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Vamos substituir a tag de extra menu e todo o IF que se segue
    # pela estrutura com block default_mobile_menu
    
    start_tag = '{% block mobile_menu_extra %}{% endblock %}'
    start_idx = content.find(start_tag)
    if start_idx == -1:
        print("start_tag não encontrado!")
        sys.exit(1)
        
    end_tag = '{% endif %}'
    # Precisamos encontrar o {% endif %} que fecha o {% if department %} ou {% elif club_context %} etc.
    # Na verdade, é o {% endif %} correspondente ao {% if department %} que no meu código começa na linha 547 e termina na 585.
    
    # Vou apenas fazer uma substituição cuidadosa.
    target_str = """                    {% block mobile_menu_extra %}{% endblock %}

                    {% if department %}"""
    
    replace_str = """                    {% block mobile_menu_extra %}{% endblock %}

                    {% block default_mobile_menu %}
                    {% if department %}"""
    
    if target_str in content:
        content = content.replace(target_str, replace_str)
        
        # Agora fechar o block default_mobile_menu após o {% endif %} final
        # O {% endif %} final desse bloco está logo acima do fechamento da div sidebar-nav
        target_end_str = """                    </form>
                    {% endif %}
                {% endif %}
            </div>"""
        
        replace_end_str = """                    </form>
                    {% endif %}
                    {% endblock %}
                {% endif %}
            </div>"""
            
        content = content.replace(target_end_str, replace_end_str)
        
        with open('templates/base.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("base.html atualizado com default_mobile_menu")
    else:
        print("Não achou o target_str no base.html")

except Exception as e:
    print(e)
