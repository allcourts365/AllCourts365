import datetime
from django.utils import timezone
from .models import Category, Match, Court, Tournament

def generate_knockout_schedule(tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        club = tournament.club

        if not tournament.start_date or not tournament.end_date:
            return False, "Torneio sem data de início ou fim definidas."
        
        courts = list(Court.objects.filter(club=club, is_knockout_court=True))
        if not courts:
            return False, "O clube não possui quadras marcadas para torneios eliminatórios."

        unscheduled_matches = list(Match.objects.filter(
            tournament=tournament, 
            is_bye=False,
            status='pending',
            scheduled_datetime__isnull=True
        ).order_by('round_number', 'id'))

        if not unscheduled_matches:
            return True, "Nenhum jogo pendente de agendamento."

        match_duration = tournament.match_duration or 90
        duration_delta = datetime.timedelta(minutes=match_duration)

        current_date = tournament.start_date
        end_date = tournament.end_date

        player_daily_matches = {}
        player_free_time = {} # Tracks when the player is next available globally

        def get_daily_availability(date_obj):
            weekday = date_obj.weekday()
            open_time = club.weekday_open if weekday < 5 else (club.saturday_open if weekday == 5 else club.sunday_open)
            close_time = club.weekday_close if weekday < 5 else (club.saturday_close if weekday == 5 else club.sunday_close)
            if not open_time or not close_time: return None, None
            
            start_dt = timezone.make_aware(datetime.datetime.combine(date_obj, open_time))
            close_dt = timezone.make_aware(datetime.datetime.combine(date_obj, close_time))
            return {c.id: start_dt for c in courts}, close_dt

        court_availability, day_close_dt = get_daily_availability(current_date)
        matches_scheduled = 0

        for match in unscheduled_matches:
            scheduled = False
            p_a_id = match.player_a_id
            p_b_id = match.player_b_id

            while not scheduled and current_date <= end_date:
                if not court_availability:
                    current_date += datetime.timedelta(days=1)
                    court_availability, day_close_dt = get_daily_availability(current_date)
                    continue

                if current_date not in player_daily_matches:
                    player_daily_matches[current_date] = {}

                count_a = player_daily_matches[current_date].get(p_a_id, 0)
                count_b = player_daily_matches[current_date].get(p_b_id, 0)

                # Regra: limite de 2 jogos por dia por atleta
                if (p_a_id and count_a >= 2) or (p_b_id and count_b >= 2):
                    current_date += datetime.timedelta(days=1)
                    court_availability, day_close_dt = get_daily_availability(current_date)
                    continue

                sorted_courts = sorted(court_availability.items(), key=lambda x: x[1])
                
                court_assigned = False
                for court_id, next_avail in sorted_courts:
                    # Garantir que nenhum jogador jogue em dois lugares ao mesmo tempo
                    time_a = player_free_time.get(p_a_id, next_avail) if p_a_id else next_avail
                    time_b = player_free_time.get(p_b_id, next_avail) if p_b_id else next_avail
                    
                    proposed_start = max(next_avail, time_a, time_b)
                    proposed_end = proposed_start + duration_delta

                    # Regra: O final do jogo não pode exceder o fechamento do clube
                    if proposed_end > day_close_dt:
                        continue 

                    match.scheduled_datetime = proposed_start
                    match.court_id = court_id
                    match.schedule_status = 'agendado'
                    match.save()

                    court_availability[court_id] = proposed_end
                    if p_a_id:
                        player_free_time[p_a_id] = proposed_end
                        player_daily_matches[current_date][p_a_id] = count_a + 1
                    if p_b_id:
                        player_free_time[p_b_id] = proposed_end
                        player_daily_matches[current_date][p_b_id] = count_b + 1
                    
                    scheduled = True
                    matches_scheduled += 1
                    court_assigned = True
                    break 

                if not court_assigned:
                    current_date += datetime.timedelta(days=1)
                    court_availability, day_close_dt = get_daily_availability(current_date)

            if not scheduled:
                return False, f"Não foi possível agendar todos os jogos. {matches_scheduled} jogos agendados."

        return True, f"{matches_scheduled} jogos agendados com sucesso."
    except Exception as e:
        return False, str(e)
