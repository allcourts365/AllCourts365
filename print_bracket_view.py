def knockout_bracket_print(request, club_id, tournament_id, category_id):
    """View read-only para impressão do chaveamento de uma categoria."""
    from .models import Club, Match
    club       = get_object_or_404(Club, id=club_id)
    tournament = get_object_or_404(club.tournaments, id=tournament_id, tournament_type='knockout', is_active=True)
    category   = get_object_or_404(tournament.categories, id=category_id)

    all_matches = list(Match.objects.filter(category=category, tournament=tournament)
                       .select_related('player_a', 'player_b', 'winner')
                       .order_by('round_number', 'position_in_bracket'))

    match_by_id = {}
    children_by_next_match = {}
    rounds_dict = {}

    num_brackets = getattr(tournament, 'number_of_brackets', 1)
    if num_brackets > 1:
        r1_matches = [m for m in all_matches if m.round_number == 1]
        total_r1 = len(r1_matches)
        if total_r1 > 0:
            matches_per_bracket = total_r1 // num_brackets
            if matches_per_bracket > 0:
                for m in r1_matches:
                    idx = m.position_in_bracket - 1
                    if idx % matches_per_bracket == 0:
                        m.bracket_label = f"Chave { (idx // matches_per_bracket) + 1 }"

    match_counter = 1
    for m in all_matches:
        m.match_number = match_counter
        match_by_id[m.id] = m
        match_counter += 1
        
        if m.next_match_id:
            if m.next_match_id not in children_by_next_match:
                children_by_next_match[m.next_match_id] = []
            children_by_next_match[m.next_match_id].append(m)
            
        if m.round_number not in rounds_dict:
            rounds_dict[m.round_number] = []
        rounds_dict[m.round_number].append(m)

    for m in all_matches:
        m.prev_match_a = None
        m.prev_match_b = None
        if m.id in children_by_next_match:
            for prev in children_by_next_match[m.id]:
                if prev.position_in_bracket % 2 != 0:
                    m.prev_match_a = prev
                else:
                    m.prev_match_b = prev

    brackets_list = []
    if all_matches:
        brackets_list.append({
            'name': category.name,
            'rounds': rounds_dict
        })

    return render(request, 'knockout_bracket_print.html', {
        'club':       club,
        'tournament': tournament,
        'category':   category,
        'brackets':   brackets_list,
    })
