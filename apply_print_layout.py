import re

filepath = 'templates/knockout_bracket_print.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace CSS
old_css = """        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #ccc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .header img {
            max-height: 60px;
        }
        .header-center {
            text-align: center;
        }
        .header-center h1 {
            margin: 0;
            font-size: 1.2rem;
            text-transform: uppercase;
        }
        .header-center p {
            margin: 2px 0;
            font-size: 0.9rem;
            color: #555;
        }"""

new_css = """        .header-page {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            page-break-after: always;
            break-after: page;
            text-align: center;
        }
        .header-page img {
            max-height: 250px;
            margin-bottom: 2rem;
        }
        .header-page h1 {
            margin: 0 0 1rem 0;
            font-size: 2.5rem;
            text-transform: uppercase;
        }
        .header-page p {
            margin: 5px 0;
            font-size: 1.5rem;
            color: #333;
        }"""

content = content.replace(old_css, new_css)

# Add page break avoid
old_wrapper = """        .matchup-wrapper {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            padding: 0.5rem 0;
            gap: 0.2rem;
        }"""

new_wrapper = """        .matchup-wrapper {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            padding: 0.5rem 0;
            gap: 0.2rem;
            page-break-inside: avoid;
            break-inside: avoid;
        }"""

content = content.replace(old_wrapper, new_wrapper)

# Replace HTML
old_html = """    <div class="header">
        <div>
            {% if club.logo %}
                <img src="{{ club.logo.url }}" alt="{{ club.name }}">
            {% else %}
                <div style="width: 60px; height: 60px; background: #eee; border-radius: 50%;"></div>
            {% endif %}
        </div>
        <div class="header-center">
            <h1>{{ tournament.name }} - {{ category.name }}</h1>
            <p>{{ club.name }} • {{ club.city|default:"-" }} • {{ club.state|default:"-" }}</p>
            <p>Chave Eliminatória</p>
        </div>
        <div>
            <img src="/static/images/logo_liga.png" alt="Liga" onerror="this.style.display='none'">
        </div>
    </div>"""

new_html = """    <div class="header-page">
        {% if club.logo %}
            <img src="{{ club.logo.url }}" alt="{{ club.name }}">
        {% else %}
            <div style="width: 250px; height: 250px; background: #eee; border-radius: 50%; margin-bottom: 2rem;"></div>
        {% endif %}
        <h1>{{ tournament.name }} - {{ category.name }}</h1>
        <p>{{ club.name }} • {{ club.city|default:"-" }} • {{ club.state|default:"-" }}</p>
        <p>Chave Eliminatória</p>
    </div>"""

content = content.replace(old_html, new_html)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Changes applied!")
