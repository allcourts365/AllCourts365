import re

with open('templates/knockout_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

css_to_add = '''
    .tabs-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 0;
        overflow-x: auto;
    }
    .tab-btn {
        background: none;
        border: none;
        color: var(--subtitle-color, #ccc);
        font-size: 1rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        cursor: pointer;
        position: relative;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: color 0.2s;
        white-space: nowrap;
    }
    .tab-btn:hover {
        color: #fff;
    }
    .tab-btn.active {
        color: var(--highlight-color, #fff);
        background: #02204c;
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
        margin-top: 0.25rem;
    }
    .tab-content {
        display: none;
    }
    .tab-content.active {
        display: block;
    }
    .info-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .info-card h3 {
        color: var(--highlight-color, #fff);
        margin-top: 0;
        font-size: 1.2rem;
    }
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
    }
    .info-item label {
        display: block;
        color: var(--subtitle-color, #ccc);
        font-size: 0.85rem;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .info-item span {
        color: #fff;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Programacao Date Tabs */
    .date-tabs {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
        border-bottom: 2px solid #ea580c; /* mockup orange line */
    }
    .date-tab-btn {
        background: none;
        border: none;
        color: var(--subtitle-color, #ccc);
        font-size: 0.9rem;
        font-weight: 700;
        padding: 0.5rem 1rem;
        cursor: pointer;
        text-align: center;
        text-transform: uppercase;
    }
    .date-tab-btn.active {
        color: #ea580c;
        border-bottom: 3px solid #ea580c;
        margin-bottom: -2px;
    }
    .date-tab-btn span.day-name { display: block; font-size: 0.8rem; opacity: 0.8; }
    
    .schedule-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .schedule-item {
        background: #fff; /* light mode as mockup */
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        color: #1e293b;
    }
    body.dark-mode .schedule-item {
        background: rgba(255,255,255,0.05);
        border-color: rgba(255,255,255,0.1);
        color: #f8fafc;
    }
    .schedule-item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        font-size: 0.85rem;
        color: #3b82f6;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .schedule-item-header .status-tag {
        background: #1e293b;
        color: #fff;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    .schedule-item-court {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 12px;
    }
    body.dark-mode .schedule-item-court { color: #94a3b8; }
    .schedule-player-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    body.dark-mode .schedule-player-row { border-color: rgba(255,255,255,0.05); }
    .schedule-player-row:last-child { border-bottom: none; }
    .player-name { font-weight: 500; }
    .player-score {
        display: flex;
        gap: 4px;
    }
    .score-box {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        font-weight: 600;
    }
    body.dark-mode .score-box { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); }
'''

if 'tabs-container' not in content:
    content = content.replace('</style>', css_to_add + '\n</style>')

grid_match = re.search(r'<div class="ko-category-grid">.*?</div>\s*</div>', content, re.DOTALL)
if grid_match:
    grid_html = grid_match.group()
else:
    grid_html = '<div class="ko-category-grid">{% for cat in categories %}...{% endfor %}</div>'

body_content = '''
<div style="margin-top: 2rem; margin-bottom: 2rem; text-align: center;">
    <h1 class="home-title" style="margin-top: 1rem; font-size: 2.2rem; margin-bottom: 0.25rem; color: var(--title-color, #fff);">{{ tournament.name }}</h1>
    <p class="home-subtitle" style="margin-bottom: 0; color: var(--subtitle-color, #ccc);">
        {{ club.name }} &bull; {{ tournament.start_date|date:"d/m/Y" }} a {{ tournament.end_date|date:"d/m/Y" }}
    </p>
</div>

<!-- Tabs -->
<div class="tabs-container" style="justify-content: center;">
    <button class="tab-btn active" onclick="openTab('tab-informacoes', this)">Informações</button>
    <button class="tab-btn" onclick="openTab('tab-inscritos', this)">Inscritos</button>
    <button class="tab-btn" onclick="openTab('tab-chaves', this)">Chaves</button>
    <button class="tab-btn" onclick="openTab('tab-programacao', this)">Programação</button>
</div>

<!-- Tab: Informações -->
<div id="tab-informacoes" class="tab-content active">
    <div class="info-card">
        <h3>Detalhes do Torneio</h3>
        <div class="info-grid">
            <div class="info-item">
                <label>Formato de Competição</label>
                <span>{{ tournament.get_competition_type_display|default:"Simples" }}</span>
            </div>
            <div class="info-item">
                <label>Formato de Jogo</label>
                <span>{{ tournament.get_set_format_display }}</span>
            </div>
            <div class="info-item">
                <label>Status</label>
                <span>{% if tournament.is_finished %}Encerrado{% else %}Em andamento{% endif %}</span>
            </div>
        </div>
    </div>
    {% if club.rules_pdf %}
    <div style="text-align: center; margin-top: 30px;">
        <a href="{{ club.rules_pdf.url }}" target="_blank" class="btn-highlight" style="display: inline-flex; align-items: center; gap: 10px; font-size: 1.1rem; padding: 12px 24px;">
            <i class="fas fa-file-pdf"></i> Baixar Regulamento
        </a>
    </div>
    {% endif %}
</div>

<!-- Tab: Inscritos -->
<div id="tab-inscritos" class="tab-content">
    <div class="info-card" style="padding: 0; overflow: hidden; max-width: 800px; margin: 0 auto;">
        <div style="padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.08); background: rgba(30, 41, 59, 0.95);">
            <h3 style="color: #fff; font-size: 1.2rem; margin: 0;">{{ all_participants.count }} Inscritos no Torneio</h3>
        </div>
        <div style="padding: 16px; overflow-y: auto; max-height: 60vh; display: flex; flex-direction: column; gap: 8px;">
            {% for cp in all_participants %}
            <div style="display: flex; align-items: center; gap: 16px; padding: 12px 16px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px;">
                <div style="flex-grow: 1;">
                    <div style="color: #f8fafc; font-size: 1.05rem; font-weight: 600;">{{ cp.player.name }}</div>
                </div>
                <div style="color: var(--highlight-color, #38bdf8); font-size: 0.9rem; font-weight: 700; background: rgba(56,189,248,0.1); padding: 4px 10px; border-radius: 12px;">
                    {{ cp.category.name }}
                </div>
            </div>
            {% empty %}
            <p style="text-align: center; color: #94a3b8; padding: 20px;">Nenhum inscrito.</p>
            {% endfor %}
        </div>
    </div>
</div>

<!-- Tab: Chaves -->
<div id="tab-chaves" class="tab-content">
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="color: var(--title-color, #fff);">Selecione a Categoria</h3>
    </div>
    ''' + grid_html + '''
</div>

<!-- Tab: Programação -->
<div id="tab-programacao" class="tab-content">
    {% if request.user.is_staff or request.user.is_superuser %}
    <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
        <form action="{% url 'clubs:generate_schedule' club.id tournament.id %}" method="post">
            {% csrf_token %}
            <button type="submit" class="btn-highlight" style="display: inline-flex; align-items: center; gap: 8px; font-size: 0.95rem; padding: 10px 20px; border-radius: 8px; cursor: pointer; border: none; background: var(--primary); color: #fff; font-weight: bold;">
                <i class="fas fa-calendar-alt"></i> Gerar Programação Automática
            </button>
        </form>
    </div>
    
    {% if messages %}
        <div style="margin-bottom: 20px;">
            {% for message in messages %}
                <div style="padding: 15px; border-radius: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.4); color: #10b981; font-weight: 600;">
                    {{ message }}
                </div>
            {% endfor %}
        </div>
    {% endif %}
    {% endif %}

    {% if not scheduled_matches %}
    <div class="info-card" style="text-align: center;">
        <p style="color: var(--subtitle-color, #ccc);">Nenhum jogo agendado no momento.</p>
    </div>
    {% else %}
    
    {% regroup scheduled_matches by scheduled_datetime.date as matches_by_date %}
    
    <div class="date-tabs">
        {% for group in matches_by_date %}
        <button class="date-tab-btn {% if forloop.first %}active{% endif %}" onclick="openDateTab('date-{{ forloop.counter }}', this)">
            <span class="day-name">{{ group.grouper|date:"D" }}</span>
            {{ group.grouper|date:"d/m/Y" }}
        </button>
        {% endfor %}
    </div>
    
    <div class="schedule-lists-container">
        {% for group in matches_by_date %}
        <div id="date-{{ forloop.counter }}" class="schedule-date-content" style="{% if not forloop.first %}display: none;{% endif %}">
            <div class="schedule-list">
                {% for match in group.list %}
                <div class="schedule-item">
                    <div class="schedule-item-header">
                        <div>
                            Jogo {{ match.match_number|default:match.id }} &bull; {{ match.scheduled_datetime|date:"H:i" }} &bull; {{ match.category.name }} &bull; {{ match.phase|default:"Fase" }}
                        </div>
                        <div class="status-tag">{% if match.status == 'completed' %}Encerrado{% else %}Agendado{% endif %}</div>
                    </div>
                    <div class="schedule-item-court">{{ match.court.name|default:"Quadra a definir" }}</div>
                    
                    <div class="schedule-player-row">
                        <div class="player-name">
                            {% if match.player_a %}
                                {{ match.player_a.name }}
                            {% else %}
                                A definir
                            {% endif %}
                        </div>
                        <div class="player-score">
                            {% if match.set1_a != None %}<div class="score-box">{{ match.set1_a }}</div>{% endif %}
                            {% if match.set2_a != None %}<div class="score-box">{{ match.set2_a }}</div>{% endif %}
                            {% if match.set3_a != None %}<div class="score-box">{{ match.set3_a }}</div>{% endif %}
                        </div>
                    </div>
                    <div class="schedule-player-row">
                        <div class="player-name">
                            {% if match.player_b %}
                                {{ match.player_b.name }}
                            {% else %}
                                A definir
                            {% endif %}
                        </div>
                        <div class="player-score">
                            {% if match.set1_b != None %}<div class="score-box">{{ match.set1_b }}</div>{% endif %}
                            {% if match.set2_b != None %}<div class="score-box">{{ match.set2_b }}</div>{% endif %}
                            {% if match.set3_b != None %}<div class="score-box">{{ match.set3_b }}</div>{% endif %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</div>

<script>
    function openTab(tabId, btn) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        btn.classList.add('active');
    }
    function openDateTab(tabId, btn) {
        document.querySelectorAll('.schedule-date-content').forEach(t => t.style.display = 'none');
        document.querySelectorAll('.date-tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(tabId).style.display = 'block';
        btn.classList.add('active');
    }
</script>
'''

# The current knockout_detail has a `.print-cover` and `ko-category-grid`
# Since I'm not totally sure of the exact regex match for `.print-cover` up to `{% endblock %}`, I will extract the blocks safely.
# Replace the container that starts with <div style="margin-top: 30px;">
new_content = re.sub(r'<div style="margin-top: 30px;">.*?{% endblock %}', body_content + '\n{% endblock %}', content, flags=re.DOTALL)

with open('templates/knockout_detail.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
