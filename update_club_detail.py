import sys

try:
    with open('templates/club_detail.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Encontrar o link Voltar (termina com </div> antes do club-header-card)
    voltar_end_idx = content.find('</div>', content.find('<div style="text-align: left; margin-bottom: 20px; margin-top: 0; padding-top: 20px;">')) + 6
    
    # Adicionar o texto Bem-vindo ali
    bem_vindo_html = """\n<div style="text-align: center; margin-top: 20px; margin-bottom: 30px;">
    <h2 style="font-size: clamp(2rem, 5vw, 3rem); font-weight: 800; color: #fff;">Bem vindo ao {{ club.name }}</h2>
</div>\n"""
    
    # 2. Encontrar o Bem-vindo antigo e remover
    old_bem_vindo_start = content.find('<div style="text-align: center; margin-top: 60px; margin-bottom: 40px;">')
    old_bem_vindo_end = content.find('</div>', old_bem_vindo_start) + 6
    
    # 3. Encontrar o card de localização antigo e substituir pelo novo
    old_loc_start = content.find('<div class="glass-card" style="padding: 30px; text-align: center; border-radius: 20px; max-width: 800px; margin: 0 auto 60px;">')
    old_loc_end = content.find('{% endblock %}', old_loc_start) # block content end
    
    new_loc_html = """<div class="desktop-3-cols" style="display: grid; gap: 20px; justify-content: center; margin-bottom: 60px;">
    <div class="glass-card" style="padding: 0; overflow: hidden; height: 100%; display: flex; flex-direction: column; border-radius: 20px; max-width: 400px; width: 100%; min-width: 300px;">
        <!-- Capa -->
        <div style="width: 100%; aspect-ratio: 4 / 1; position: relative; background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(0,0,0,0.5)); border-bottom: 1px solid rgba(255,255,255,0.1); flex-shrink: 0;">
            <div style="width: 100%; height: 100%; overflow: hidden; position: absolute; top: 0; left: 0;">
                {% if club.card_image %}
                    <img src="{{ club.card_image.url }}" style="width: 100%; height: 100%; object-fit: contain; opacity: 0.5; transform: scale(calc({{ club.card_image_size|default:100 }} / 100)); transform-origin: center;">
                {% elif club.background_image %}
                    <img src="{{ club.background_image.url }}" style="width: 100%; height: 100%; object-fit: contain; opacity: 0.5; transform: scale(calc({{ club.card_image_size|default:100 }} / 100)); transform-origin: center;">
                {% endif %}
            </div>
            
            <!-- Logo overlapping -->
            <div style="position: absolute; bottom: -45px; left: 50%; transform: translateX(-50%); width: 90px; height: 90px; border-radius: 50%; background: #1a1a2e; border: 3px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                <i class="fas fa-map-marked-alt" style="font-size: 2.2rem; color: var(--highlight-color);"></i>
            </div>
        </div>

        <!-- Info -->
        <div style="padding: 60px 20px 30px 20px; text-align: center; display: flex; flex-direction: column; flex-grow: 1;">
            <h3 style="margin-bottom: 10px; font-size: 1.5rem; font-weight: 800; color: #fff; text-transform: uppercase;">Localização</h3>
            <p style="margin-bottom: 20px; color: var(--subtitle-color); font-size: 0.95rem;">{{ club.address|default:"Endereço não cadastrado" }}</p>
            {% if club.address %}
            <div style="flex-grow: 1; border-radius: 15px; overflow: hidden; background: rgba(255,255,255,0.05); min-height: 250px;">
                <iframe
                  width="100%"
                  height="100%"
                  style="border:0; width: 100%; height: 100%; min-height: 250px;"
                  loading="lazy"
                  allowfullscreen
                  referrerpolicy="no-referrer-when-downgrade"
                  src="https://maps.google.com/maps?q={{ club.address|urlencode }}&hl=pt&z=14&output=embed">
                </iframe>
            </div>
            {% endif %}
        </div>
    </div>
</div>
"""
    
    # Reconstruindo o arquivo
    part1 = content[:voltar_end_idx] + bem_vindo_html + content[voltar_end_idx:old_bem_vindo_start]
    part2 = new_loc_html + content[old_loc_end:]
    
    new_content = part1 + part2
    
    with open('templates/club_detail.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Sucesso!")
except Exception as e:
    print(e)
