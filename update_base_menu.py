import sys

try:
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Procurando a tag user-name-label
    search_str = 'class="user-name-label"'
    idx1 = content.find(search_str)
    
    if idx1 != -1:
        # Encontra o fechamento da div
        idx2 = content.find('</div>', idx1) + 6
        
        # Insere o block
        block_str = '\n                    {% block mobile_menu_extra %}{% endblock %}\n'
        if block_str not in content:
            new_content = content[:idx2] + block_str + content[idx2:]
            with open('templates/base.html', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Block mobile_menu_extra inserido com sucesso no base.html!")
        else:
            print("Block já existe no base.html.")
    else:
        print("user-name-label não encontrado.")

except Exception as e:
    print(e)
