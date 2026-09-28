import sys

try:
    with open('templates/athlete_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Encontrar o lugar onde colocar o Bem vindo (antes do club-header-card)
    card_start = content.find('<div class="glass-card club-header-card"')
    
    bem_vindo_html = """<div style="text-align: center; margin-top: 20px; margin-bottom: 30px;">
    <h2 style="font-size: clamp(2rem, 5vw, 3rem); font-weight: 800; color: #fff;">Bem vindo ao Painel Administrativo de Atleta</h2>
</div>
"""
    
    # 2. Remover o Bem vindo antigo do meio da tela
    old_title = '<h2 style="font-size: 2rem; margin: 0; text-align: center;">Bem vindo ao Painel Administrativo de Atleta</h2>'
    
    # Executando apenas se o texto antigo existir, caso contrário o script não quebra
    if old_title in content:
        content = content.replace(old_title, '')
        
        # Como substituí o title por vazio, posso ter deixado uma div solta, mas ela tem o club-switcher. 
        # Vou deixar a div do club-switcher, pois não pediram para tirar o club-switcher.
        
        # Colocando o Bem vindo novo
        content = content[:card_start] + bem_vindo_html + content[card_start:]
        
        with open('templates/athlete_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Alteração feita!")
    else:
        print("Título antigo não encontrado. Talvez já tenha sido removido.")

except Exception as e:
    print(e)
