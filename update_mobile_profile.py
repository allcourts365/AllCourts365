import sys

try:
    with open('templates/athlete_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Ajustar o padding do glass-card do Perfil Mobile
    target_card = '<div class="glass-card" style="padding: 25px 20px; border-radius: 16px;">'
    replace_card = '<div class="glass-card" style="padding: 25px 8px; border-radius: 16px;">'
    content = content.replace(target_card, replace_card)

    # 2. Ajustar o gap entre os campos
    target_gap = '<div style="display: flex; flex-direction: column; gap: 20px;">'
    # Nós vamos remover o gap e forçar a margem ser menor nos campos em si.
    replace_gap = '<div style="display: flex; flex-direction: column; gap: 0;">'
    content = content.replace(target_gap, replace_gap)

    # Precisamos fazer isso apenas para a parte MOBILE do Meu Perfil.
    # O jeito mais seguro é adicionar uma classe CSS específica ou estilo inline nas divs custom-form-group do form-mobile.
    # Em vez de tentar regex complicado, vou apenas colocar uma tag `<style>` logo acima dessa `vinculos-mobile`
    
    style_tag = """
        <style>
            .vinculos-mobile .profile-form .custom-form-group {
                margin-bottom: 10px !important;
            }
            .vinculos-mobile .profile-form input,
            .vinculos-mobile .profile-form select {
                padding: 12px 10px !important;
            }
        </style>
        <div class="vinculos-mobile">
"""
    if '<style>' not in content.replace(' ', ''): # just checking if I already added it
        pass

    content = content.replace('        <div class="vinculos-mobile">', style_tag)

    with open('templates/athlete_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Modificações feitas com sucesso!")

except Exception as e:
    print(e)
