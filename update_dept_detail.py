import sys

try:
    with open('templates/department_detail.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add "Bem vindo" above the card
    voltar_end_idx = content.find('</div>', content.find('<div style="text-align: left; margin-bottom: 20px; margin-top: 0; padding-top: 20px;">')) + 6
    bem_vindo_html = """\n<div style="text-align: center; margin-top: 20px; margin-bottom: 30px;">
    <h2 style="font-size: clamp(2rem, 5vw, 3rem); font-weight: 800; color: #fff;">Bem vindo ao {{ department.name }}</h2>
</div>\n"""
    
    # Check if not already added
    if "Bem vindo ao {{ department.name }}" not in content:
        content = content[:voltar_end_idx] + bem_vindo_html + content[voltar_end_idx:]

    # 2. Remove the old "Bem-vindo aos Torneios" if present
    old_title_str = '<h2 style="font-size: clamp(1.5rem, 4vw, 2rem); margin-bottom: 20px; border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 10px; text-align: center;">Bem-vindo aos Torneios do {{ department.name }}</h2>'
    content = content.replace(old_title_str, '')

    # 3. Remove "Notícias" button
    import re
    news_btn_pattern = re.compile(r'<a href="{% url \'clubs:news_list\' club\.id %}"[\s\S]*?Notícias {{ club\.name }}\s*</a>')
    content = re.sub(news_btn_pattern, '', content)

    # 4. Make Ranking cards clickable
    ranking_card_start = '<div class="glass-card" style="padding: 25px; border-radius: 12px; display: flex; flex-direction: column;">'
    new_ranking_card = '<div class="glass-card" onclick="window.location.href=\'{% url \'clubs:ranking_detail\' club.id t.id %}\'" style="padding: 25px; border-radius: 12px; display: flex; flex-direction: column; cursor: pointer; transition: transform 0.2s;" onmouseover="this.style.transform=\'translateY(-5px)\'" onmouseout="this.style.transform=\'translateY(0)\'">'
    
    # We have two tabs, one for rankings, one for knockouts. They use the SAME exact card HTML to start.
    # We should distinguish them by splitting the content or using regex.
    # The first loop is `{% for t in rankings %}`
    rankings_block_start = content.find('{% for t in rankings %}')
    rankings_block_end = content.find('{% empty %}', rankings_block_start)
    
    if rankings_block_start != -1 and rankings_block_end != -1:
        rankings_block = content[rankings_block_start:rankings_block_end]
        rankings_block = rankings_block.replace(ranking_card_start, new_ranking_card)
        content = content[:rankings_block_start] + rankings_block + content[rankings_block_end:]
        
    # The second loop is `{% for t in knockouts %}`
    new_knockout_card = '<div class="glass-card" onclick="window.location.href=\'{% url \'clubs:knockout_detail\' club.id t.id %}\'" style="padding: 25px; border-radius: 12px; display: flex; flex-direction: column; cursor: pointer; transition: transform 0.2s;" onmouseover="this.style.transform=\'translateY(-5px)\'" onmouseout="this.style.transform=\'translateY(0)\'">'
    knockouts_block_start = content.find('{% for t in knockouts %}')
    knockouts_block_end = content.find('{% empty %}', knockouts_block_start)
    
    if knockouts_block_start != -1 and knockouts_block_end != -1:
        knockouts_block = content[knockouts_block_start:knockouts_block_end]
        knockouts_block = knockouts_block.replace(ranking_card_start, new_knockout_card)
        content = content[:knockouts_block_start] + knockouts_block + content[knockouts_block_end:]

    with open('templates/department_detail.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Modificações no department_detail.html aplicadas com sucesso.")

except Exception as e:
    print("Erro:", e)
