with open('clubs/admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("'contact_whatsapp', 'whatsapp_group_link', 'fee_observation'", "'contact_whatsapp', 'whatsapp_group_link', 'message_for_athletes', 'fee_observation'")

with open('clubs/admin.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Admin updated!')
