from news.admin import BroadcastMessageAdmin
from news.models import BroadcastMessage
from clubs.models import Department
from django.contrib.auth.models import User
from django.contrib.admin.sites import site
from core.models import Message
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings") # or whatever the settings are
# Actually this script will be executed via manage.py shell, so I don't need django setup.

def test():
    admin_user = User.objects.filter(is_staff=True).first()
    dept = Department.objects.first()
    msg = BroadcastMessage(subject='Test Admin', body='Hello', department=dept, sender=admin_user)
    
    class DummyRequest: pass
    req = DummyRequest()
    req.user = admin_user
    
    ba = BroadcastMessageAdmin(BroadcastMessage, site)
    ba.save_model(req, msg, None, False)
    print('Messages generated:', Message.objects.filter(broadcast=msg).count())

test()
