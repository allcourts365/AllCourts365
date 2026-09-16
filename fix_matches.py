import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allcourts365.settings')
django.setup()

from clubs.models import Match

matches = Match.objects.filter(status='completed', schedule_status='aguardando_adversario')
count = matches.count()
for m in matches:
    m.schedule_status = 'agendado'
    m.save(update_fields=['schedule_status'])

print(f"Fixed {count} matches.")
