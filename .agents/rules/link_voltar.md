# Padrão para Links de "Voltar"

Nas páginas que possuem um link de "Voltar" (seja "Voltar à Home" ou "Voltar para [Clube]"), o padrão visual e de posicionamento oficial deve seguir o formato estabelecido na página de notícias dos clubes (`news_list.html`).

## Regras de Estilo e Posição:
- O link não deve ter margens customizadas à esquerda (`margin-left: 20px`), ele deve acompanhar o alinhamento natural do container onde o título da página está.
- O HTML do link deve ser `<a href="..." style="display: inline-flex; align-items: center; gap: 8px; color: var(--highlight-color, #00BFFF); text-decoration: none; font-size: 0.95rem; font-weight: 600; margin-bottom: 20px;">`
- Ele deve ficar logo acima do título principal da página (`<h1>`).
- Se houver ícone de seta, usar `<i class="fas fa-arrow-left"></i>` ou simplesmente `←`.

Sempre aplique este padrão ao adicionar ou corrigir links de navegação para voltar páginas no AllCourts365.
