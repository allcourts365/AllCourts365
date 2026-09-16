import re

with open('templates/athlete_calendar.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('na ${ev.court_name}', '${ev.court_name ? \'na \' + ev.court_name : \'(Quadra a definir)\'}')

with open('templates/athlete_calendar.html', 'w', encoding='utf-8') as f:
    f.write(content)
