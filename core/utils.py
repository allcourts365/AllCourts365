import unicodedata
import re
from django.contrib.auth.models import User

def generate_friendly_username(name, email=''):
    """
    Gera um nome de usuário amigável com base no nome e e-mail (fallback).
    Exemplo: "João Silva" -> "joaosilva", "joaosilva1", etc.
    """
    base_username = ''
    if name:
        base_username = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
        base_username = re.sub(r'[^\w\s]', '', base_username).strip().lower().replace(' ', '')
    
    if not base_username and email:
        base_username = email.split('@')[0]
        base_username = re.sub(r'[^\w\s]', '', base_username).strip().lower().replace(' ', '')
        
    if not base_username:
        base_username = 'usuario'
        
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
        
    return username
