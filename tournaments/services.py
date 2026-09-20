import pandas as pd
import math
import random
from .models import Tournament, Category, Player, CategoryPlayer, Match

def generate_round_robin_matches(category, players):
    """
    Generates round-robin matches for a list of players in a category.
    Handles 'Bye' for odd number of players.
    """
    if not players:
        return

    # If odd number of players, add a None (Bye)
    if len(players) % 2 != 0:
        players.append(None)

    num_players = len(players)
    num_rounds = num_players - 1
    half_size = num_players // 2

    matches_to_create = []

    for round_idx in range(num_rounds):
        round_number = round_idx + 1
        for i in range(half_size):
            player_a = players[i]
            player_b = players[num_players - 1 - i]
            
            if player_a is not None or player_b is not None:
                matches_to_create.append(
                    Match(
                        category=category,
                        round_number=round_number,
                        player_a=player_a,
                        player_b=player_b,
                        status='pending'
                    )
                )

        # Rotate players: keep the first player fixed, rotate the rest clockwise
        players = [players[0]] + [players[-1]] + players[1:-1]

    Match.objects.bulk_create(matches_to_create)

def process_excel_tournament(file, tournament):
    """
    Process an Excel file. Unified logic:
    If 'Confrontos' sheet exists and has data -> In Progress Tournament
    Otherwise -> New Tournament (Generates Round-Robin automatically)
    """
    xls = pd.ExcelFile(file)
    messages_list = []
    
    from django.contrib.auth.models import User
    from django.utils.crypto import get_random_string
    from allauth.account.models import EmailAddress
    from django.core.mail import send_mail
    from django.conf import settings
    
    # 1. Process Cadastro
    df_cadastro = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    if len(df_cadastro.columns) < 2:
        raise ValueError("A aba de Cadastro precisa ter pelo menos 2 colunas: Nome e Categoria.")
        
    names = df_cadastro.iloc[:, 0].astype(str).str.strip()
    categories = df_cadastro.iloc[:, 1].astype(str).str.strip()
    
    emails = None
    if len(df_cadastro.columns) > 2:
        emails = df_cadastro.iloc[:, 2].astype(str).str.strip()
        
    verificados = None
    if len(df_cadastro.columns) > 3:
        verificados = df_cadastro.iloc[:, 3].astype(str).str.strip()
    
    category_players_map = {}
    
    # Check if tournament has club
    club = getattr(tournament, 'club', None)
    
    for i in range(len(names)):
        name = names[i]
        cat_name = categories[i]
        
        if pd.isna(name) or name == 'nan' or pd.isna(cat_name) or cat_name == 'nan':
            continue
            
        category, _ = Category.objects.get_or_create(tournament=tournament, name=cat_name)
        
        pemail = None
        if emails is not None:
            val = emails[i]
            if not pd.isna(val) and val != 'nan' and val:
                pemail = val
                
        pverificado = False
        if verificados is not None:
            val = verificados[i].lower()
            if not pd.isna(val) and val != 'nan' and val in ['sim', 's', 'yes', 'y']:
                pverificado = True
                
        player = None
        user = None
        
        if pemail:
            # Tentar buscar usuario existente
            user = User.objects.filter(email=pemail).first() or User.objects.filter(username=pemail).first()
            
            if user:
                # Tenta encontrar o player já vinculado a esse usuário
                existing_player = Player.objects.filter(user=user).first()
                if existing_player:
                    player = existing_player
                    
        if not player:
            # Cria ou pega o player. Adiciona o club se existir (pra RankingTournament deve existir)
            if club:
                player, _ = Player.objects.get_or_create(club=club, name=name)
            else:
                player, _ = Player.objects.get_or_create(name=name)
                
        if pemail and not player.user:
            if not user:
                # Criar novo usuário
                from core.utils import generate_friendly_username
                friendly_username = generate_friendly_username(name, pemail)
                initial_password = get_random_string(8)
                user = User.objects.create_user(username=friendly_username, email=pemail, password=initial_password)
                user.first_name = name.split()[0]
                user.save()
                
                # Definir o e-mail no allauth e verificar
                email_address = EmailAddress.objects.create(
                    user=user,
                    email=pemail,
                    verified=pverificado,
                    primary=True
                )
                
                # Enviar email com senha
                club_name = club.name if club else "AllCourts365"
                subject = f"Bem-vindo(a) ao {club_name}"
                message = (
                    f"Olá {name},\n\n"
                    f"Seu cadastro no {tournament.name} do {club_name} foi criado.\n\n"
                    f"Entre com seu usuário {friendly_username} ou seu email {pemail}.\n"
                    f"Sua senha inicial de acesso é: {initial_password}\n\n"
                    f"Sugerimos que ao acessar o Painel de Atleta na aba Meu Perfil faça a redefinição de sua senha.\n\n"
                    f"Obrigado e um ótimo torneio!\n\n"
                )
                if pverificado:
                    message += "Sua conta já está ativada e pronta para uso."
                else:
                    message += "Você receberá em instantes um e-mail com um link para confirmar e ativar sua conta."
                    
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [pemail],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                    
                # Se nao verificado, enviar email confirmacao do Allauth
                if not pverificado:
                    try:
                        # Para enviar sem request explícito, passamos None
                        email_address.send_confirmation(None)
                    except Exception:
                        pass
                        
            # Vincula o usuario
            player.user = user
            player.save()
            
        if user and club:
            from core.models import PlayerLinkRequest
            PlayerLinkRequest.objects.get_or_create(
                user=user,
                club=club,
                player=player,
                defaults={'status': 'approved'}
            )
            
        CategoryPlayer.objects.get_or_create(category=category, player=player)
        
        if category not in category_players_map:
            category_players_map[category] = []
        category_players_map[category].append(player)

    # 2. Check if Confrontos exists and has data
    has_confrontos = False
    matches_created = 0
    matches_updated = 0
    if len(xls.sheet_names) > 1:
        df_confrontos = pd.read_excel(xls, sheet_name=xls.sheet_names[1])
        if not df_confrontos.empty and len(df_confrontos.columns) >= 5:
            has_confrontos = True
            
            for index, row in df_confrontos.iterrows():
                cat_name = str(row.iloc[0]).strip()
                player_a_name = str(row.iloc[2]).strip()
                player_b_name = str(row.iloc[3]).strip()
                resultado = str(row.iloc[4]).strip().lower().replace(" ", "")

                if pd.isna(cat_name) or cat_name == 'nan': continue

                category = Category.objects.filter(tournament=tournament, name__iexact=cat_name).first()
                if not category:
                    category = Category.objects.filter(tournament=tournament, name__iexact=f"Categoria {cat_name}").first()
                if not category and len(cat_name) <= 3:
                    category = Category.objects.filter(tournament=tournament, name__iendswith=f" {cat_name}").first()

                if not category:
                    messages_list.append(f"Linha {index+2}: Categoria não encontrada -> {cat_name}")
                    continue

                p_a = None
                if player_a_name and player_a_name.lower() not in ('nan', 'bye', 'folga'):
                    p_a = Player.objects.filter(name__iexact=player_a_name).first()
                    if not p_a:
                        messages_list.append(f"Linha {index+2}: Atleta A não encontrado -> {player_a_name}")
                        continue
                        
                p_b = None
                if player_b_name and player_b_name.lower() not in ('nan', 'bye', 'folga'):
                    p_b = Player.objects.filter(name__iexact=player_b_name).first()
                    if not p_b:
                        messages_list.append(f"Linha {index+2}: Atleta B não encontrado -> {player_b_name}")
                        continue

                sets_a = 0
                sets_b = 0
                status = 'pending'
                winner = None

                if resultado and resultado not in ('nan', '', '0x0', '-'):
                    status = 'completed'
                    if 'x' in resultado:
                        try:
                            parts = resultado.split('x')
                            sets_a = int(parts[0])
                            sets_b = int(parts[1])
                            if sets_a > sets_b:
                                winner = p_a
                            elif sets_b > sets_a:
                                winner = p_b
                        except ValueError:
                            messages_list.append(f"Linha {index+2}: Placar inválido -> {resultado}")
                            status = 'pending'
                    elif 'v.o' in resultado or 'w.o' in resultado or 'wo' in resultado:
                        sets_a, sets_b = 2, 0
                        winner = p_a
                    else:
                        messages_list.append(f"Linha {index+2}: Placar em formato desconhecido -> {resultado}")
                        status = 'pending'
                
                match = Match.objects.filter(
                    category=category,
                    player_a=p_a,
                    player_b=p_b
                ).first()
                
                if not match:
                    match = Match.objects.filter(
                        category=category,
                        player_a=p_b,
                        player_b=p_a
                    ).first()
                    
                    if match:
                        sets_a, sets_b = sets_b, sets_a
                
                if not match:
                    try:
                        round_number = int(float(row.iloc[1]))
                    except (ValueError, TypeError):
                        round_number = 1
                        
                    match = Match.objects.create(
                        category=category,
                        round_number=round_number,
                        player_a=p_a,
                        player_b=p_b,
                        sets_a=sets_a,
                        sets_b=sets_b,
                        status=status,
                        winner=winner
                    )
                    matches_created += 1
                else:
                    if status == 'completed' or resultado == '0x0':
                        match.sets_a = sets_a
                        match.sets_b = sets_b
                        match.status = status
                        match.winner = winner
                        match.save()
                        matches_updated += 1

    if not has_confrontos:
        for category, players in category_players_map.items():
            Match.objects.filter(category=category).delete()
            generate_round_robin_matches(category, players)
        return True, "Novo Ranking gerado com sucesso! Todos contra todos criados.", messages_list
    
    return True, f"Ranking em andamento atualizado: {matches_created} jogos criados, {matches_updated} atualizados.", messages_list

def get_seed_order(n):
    """Returns the standard bracket ordering for N players (N must be power of 2)"""
    if n == 1:
        return [1]
    half = get_seed_order(n // 2)
    res = []
    for s in half:
        res.append(s)
        res.append(n - s + 1)
    return res

def process_excel_knockout(file, tournament):
    df = pd.read_excel(file)
    
    if 'Nome' not in df.columns:
        return False, "A coluna 'Nome' é obrigatória.", []
        
    has_seed = 'Cabeça de Chave' in df.columns
    has_cat = 'Categoria' in df.columns
    
    players_data = []
    for _, row in df.iterrows():
        name = str(row['Nome']).strip()
        if not name or name.lower() == 'nan':
            continue
            
        is_seed = False
        if has_seed and pd.notna(row['Cabeça de Chave']):
            val = str(row['Cabeça de Chave']).strip().upper()
            if val == 'X':
                is_seed = True
                
        cat = None
        if has_cat and pd.notna(row['Categoria']):
            cat = str(row['Categoria']).strip()
            if cat.lower() == 'nan':
                cat = None
                
        players_data.append({'name': name, 'is_seed': is_seed, 'category': cat})
        
    if not players_data:
        return False, "Nenhum atleta encontrado na planilha.", []
        
    # Delete existing matches and categories for this tournament to rebuild bracket
    Match.objects.filter(tournament=tournament).delete()
    Category.objects.filter(tournament=tournament).delete()
    
    num_brackets = getattr(tournament, 'number_of_brackets', 1)
    if num_brackets < 1:
        num_brackets = 1

    # Group players
    groups = {}
    if has_cat:
        for pd_item in players_data:
            cat_name = pd_item['category']
            if not cat_name:
                cat_name = "Sem Categoria"
            if cat_name not in groups:
                groups[cat_name] = []
            groups[cat_name].append(pd_item)
    else:
        groups[None] = players_data
        
    for cat_name, group_players in groups.items():
        category_obj = None
        if cat_name is not None:
            category_obj, _ = Category.objects.get_or_create(tournament=tournament, name=cat_name)
            
        player_objs = []
        seeded_players = []
        unseeded_players = []
        
        for pd_item in group_players:
            player, _ = Player.objects.get_or_create(name=pd_item['name'])
            if category_obj:
                CategoryPlayer.objects.get_or_create(category=category_obj, player=player)
                
            player_objs.append(player)
            if pd_item['is_seed']:
                seeded_players.append(player)
            else:
                unseeded_players.append(player)
                
        # Randomize unseeded
        random.shuffle(unseeded_players)
        
        num_players = len(player_objs)
        bracket_size = 2 ** math.ceil(math.log2(max(2, num_players)))
        
        # Pad players to power of 2
        padded_players = seeded_players + unseeded_players
        while len(padded_players) < bracket_size:
            padded_players.append(None)
            
        seed_pattern = get_seed_order(bracket_size)
        
        slots = [None] * bracket_size
        for i, rank in enumerate(seed_pattern):
            slots[i] = padded_players[rank - 1]
            
        def get_phase_name(round_num, total_rounds):
            rounds_left = total_rounds - round_num
            
            if rounds_left == 0: return "Final"
            if rounds_left == 1: return "Semifinal"
            if rounds_left == 2: return "Quartas de Final"
            if rounds_left == 3: return "Oitavas de Final"
            
            if num_brackets == 1:
                if rounds_left == 4: return "Dezesseis-avos"
                if rounds_left == 5: return "Trinta-e-dois-avos"
                
            return f"{round_num}ª Rodada"
            
        def build_tree(round_num, max_rounds, match_pos, next_m):
            m = Match.objects.create(
                tournament=tournament,
                category=category_obj,
                round_number=round_num,
                phase=get_phase_name(round_num, max_rounds),
                next_match=next_m,
                position_in_bracket=match_pos
            )
            if round_num > 1:
                build_tree(round_num - 1, max_rounds, match_pos * 2 - 1, m)
                build_tree(round_num - 1, max_rounds, match_pos * 2, m)
            return m
            
        num_rounds = int(math.log2(bracket_size))
        build_tree(num_rounds, num_rounds, 1, None)
        
        r1_matches = Match.objects.filter(tournament=tournament, category=category_obj, round_number=1).order_by('position_in_bracket')
        
        for i, match in enumerate(r1_matches):
            p1 = slots[i*2]
            p2 = slots[i*2 + 1]
            
            match.player_a = p1
            match.player_b = p2
            
            if not p1 or not p2:
                if not p1 and not p2:
                    match.status = 'cancelled'
                else:
                    match.status = 'completed'
                    match.winner = p1 if p1 else p2
                    if match.next_match:
                        nm = match.next_match
                        if match.position_in_bracket % 2 != 0:
                            nm.player_a = match.winner
                        else:
                            nm.player_b = match.winner
                        nm.save()
            match.save()
            
    return True, f"Torneio Eliminatório gerado com sucesso! Processado em {len(groups)} grupos/categorias com {len(players_data)} atletas no total.", []
