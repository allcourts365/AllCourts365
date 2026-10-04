import os
import requests
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Configurações da sua API Não-Oficial (Ex: Evolution API)
# Você deve configurar essas variáveis no seu arquivo .env ou settings.py
WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL', 'http://localhost:8080/message/sendText/AllCourts')
WHATSAPP_API_KEY = os.environ.get('WHATSAPP_API_KEY', 'sua_apikey_aqui')

def send_whatsapp_message(phone_or_group_id, message):
    """
    Envia uma mensagem de texto via WhatsApp (Evolution API / W-API).
    """
    if not WHATSAPP_API_URL or not WHATSAPP_API_KEY:
        logger.warning("WhatsApp API não configurada. Mensagem não enviada.")
        return False

    headers = {
        'apikey': WHATSAPP_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "number": phone_or_group_id, # Pode ser número ex: 5511999999999 ou ID do grupo (120363@g.us)
        "text": message
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar WhatsApp: {e}")
        return False

def notify_match_scheduled(match):
    """
    Monta a mensagem e envia para o grupo do torneio (se houver).
    """
    if not match.scheduled_datetime or not match.court:
        return

    # Busca o link do grupo do torneio (ou um número fixo para testes)
    # Por enquanto, se o torneio tiver um 'whatsapp_group_link', poderíamos extrair o ID,
    # Mas em APIs como Evolution, você precisa do Group ID interno (ex: 120363...123@g.us)
    # Recomendação: Adicionar um campo `whatsapp_group_id` no modelo Tournament ou Club.
    
    # Para exemplo, vamos supor que exista uma variável global ou usemos um número de teste.
    target_number = os.environ.get('DEFAULT_WHATSAPP_GROUP_ID', '5511999999999') 

    date_str = match.scheduled_datetime.astimezone(timezone.get_current_timezone()).strftime('%d/%m/%Y às %H:%M')
    player_a_name = match.player_a.name if match.player_a else "A definir"
    player_b_name = match.player_b.name if match.player_b else "A definir"
    tournament_name = match.tournament.name if match.tournament else "Torneio"

    msg = f"🎾 *NOVO JOGO AGENDADO* 🎾\n\n"
    msg += f"🏆 *{tournament_name}*\n"
    msg += f"🏟️ *Quadra:* {match.court.name}\n"
    msg += f"📅 *Data:* {date_str}\n\n"
    msg += f"🏸 *{player_a_name}* 🆚 *{player_b_name}*\n\n"
    msg += f"Em breve, o link público da agenda será adicionado aqui!"

    send_whatsapp_message(target_number, msg)

def notify_match_updated(match):
    """
    Notifica se o jogo mudou de horário ou quadra.
    """
    if not match.scheduled_datetime or not match.court:
        return
        
    target_number = os.environ.get('DEFAULT_WHATSAPP_GROUP_ID', '5511999999999') 

    date_str = match.scheduled_datetime.astimezone(timezone.get_current_timezone()).strftime('%d/%m/%Y às %H:%M')
    player_a_name = match.player_a.name if match.player_a else "A definir"
    player_b_name = match.player_b.name if match.player_b else "A definir"
    
    msg = f"⚠️ *ATUALIZAÇÃO DE JOGO* ⚠️\n\n"
    msg += f"O jogo entre *{player_a_name}* e *{player_b_name}* foi alterado.\n\n"
    msg += f"🏟️ *Nova Quadra:* {match.court.name}\n"
    msg += f"📅 *Novo Horário:* {date_str}\n"

    send_whatsapp_message(target_number, msg)
