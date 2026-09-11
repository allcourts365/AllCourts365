import os
import django

# Define as configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allcourts365.settings')
django.setup()

from core.models import Message

def limpar_mensagens():
    # Busca todas as mensagens que ficaram orfãs (sem partida e sem o novo vínculo de broadcast)
    mensagens_fantasmas = Message.objects.filter(related_match__isnull=True, broadcast__isnull=True)
    
    count = mensagens_fantasmas.count()
    print(f"Mensagens órfãs encontradas: {count}")
    
    if count > 0:
        mensagens_fantasmas.delete()
        print("Limpeza concluída com sucesso!")
    else:
        print("Nenhuma mensagem precisava ser limpa.")

if __name__ == "__main__":
    limpar_mensagens()
