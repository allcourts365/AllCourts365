import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allcourts365.settings')
django.setup()

from django.contrib.auth.models import User

user = User.objects.filter(username='AdminTC22A').first() or User.objects.filter(is_staff=True).last()

print(f"User: {user.username}")
print(f"is_staff: {user.is_staff}")
print(f"groups: {list(user.groups.values_list('name', flat=True))}")
print(f"managed_clubs: {list(user.managed_clubs.values_list('name', flat=True))}")
print(f"has profile: {hasattr(user, 'profile')}")
if hasattr(user, 'profile'):
    print(f"use_modern_admin: {user.profile.use_modern_admin}")
