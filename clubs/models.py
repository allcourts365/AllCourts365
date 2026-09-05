from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Club(models.Model):
    POSITION_CHOICES = [
        ('top-left', 'Superior Esquerdo'),
        ('top-right', 'Superior Direito'),
        ('bottom-left', 'Inferior Esquerdo'),
        ('bottom-right', 'Inferior Direito'),
        ('center', 'Centro'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nome do Clube")
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name="Site do Clube")
    logo = models.ImageField(upload_to='clubs/logos/', null=True, blank=True, verbose_name="Logotipo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    address = models.CharField(max_length=300, blank=True, verbose_name="Endereço")
    administrators = models.ManyToManyField(User, related_name='managed_clubs', blank=True, verbose_name="Administradores")
    
    # Configurações Visuais Específicas do Clube (Sobrescrevem o Global se preenchidas)
    background_image = models.ImageField(upload_to='clubs/backgrounds/', null=True, blank=True, verbose_name="Imagem de Fundo")
    background_color = models.CharField(max_length=7, null=True, blank=True, verbose_name="Cor de Fundo Fixa (Hex)")
    overlay_color = models.CharField(max_length=7, null=True, blank=True, verbose_name="Cor do Fumê (Overlay)")
    overlay_opacity = models.FloatField(null=True, blank=True, verbose_name="Opacidade do Fumê (0.0 a 1.0)")
    
    highlight_color = models.CharField(max_length=7, null=True, blank=True, verbose_name="Cor de Destaque")
    title_color = models.CharField(max_length=7, null=True, blank=True, verbose_name="Cor do Título Principal")
    subtitle_color = models.CharField(max_length=7, null=True, blank=True, verbose_name="Cor do Subtítulo")
    
    watermark_image = models.ImageField(upload_to='clubs/watermarks/', null=True, blank=True, verbose_name="Marca d'Água do Clube")
    watermark_position = models.CharField(max_length=20, choices=POSITION_CHOICES, null=True, blank=True, verbose_name="Posição da Marca d'Água")
    watermark_opacity = models.FloatField(null=True, blank=True, verbose_name="Opacidade da Marca d'Água")
    watermark_size_percent = models.IntegerField(null=True, blank=True, verbose_name="Tamanho da Marca d'Água (%)")
    
    # Horários de Expediente
    weekday_open = models.TimeField(null=True, blank=True, verbose_name="Abertura (Dias de Semana)")
    weekday_close = models.TimeField(null=True, blank=True, verbose_name="Fechamento (Dias de Semana)")
    saturday_open = models.TimeField(null=True, blank=True, verbose_name="Abertura (Sábados)")
    saturday_close = models.TimeField(null=True, blank=True, verbose_name="Fechamento (Sábados)")
    sunday_open = models.TimeField(null=True, blank=True, verbose_name="Abertura (Domingos/Feriados)")
    sunday_close = models.TimeField(null=True, blank=True, verbose_name="Fechamento (Domingos/Feriados)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Clube"
        verbose_name_plural = "Clubes"

class Court(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='courts', verbose_name="Clube")
    name = models.CharField(max_length=100, verbose_name="Nome da Quadra")
    is_ranking_court = models.BooleanField(default=False, verbose_name="Usada para Jogos de Ranking?")

    def __str__(self):
        return f"{self.name} ({self.club.name})"

    class Meta:
        verbose_name = "Quadra"
        verbose_name_plural = "Quadras"

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player_profile', verbose_name="Usuário do Sistema")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='players', verbose_name="Clube")
    name = models.CharField(max_length=200, verbose_name="Nome do Atleta")

    def __str__(self):
        return f"{self.name} ({self.club.name})"
    
    class Meta:
        unique_together = ('club', 'name')
        verbose_name = "Atleta"
        verbose_name_plural = "Atletas"

class Tournament(models.Model):
    TOURNAMENT_TYPES = [
        ('ranking', 'Ranking Contínuo'),
        ('knockout', 'Torneio Eliminatório'),
    ]
    COMPETITION_TYPES = [
        ('simples', 'Simples'),
        ('duplas', 'Duplas'),
    ]
    SET_FORMATS = [
        ('3_normal', 'Melhor de 3 Sets Normal'),
        ('3_super', 'Melhor de 3 Sets (3º Set é Super Tiebreak)'),
        ('5_normal', 'Melhor de 5 Sets Normal'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='tournaments', verbose_name="Clube")
    name = models.CharField(max_length=200, verbose_name="Nome do Torneio/Ranking")
    tournament_type = models.CharField(max_length=20, choices=TOURNAMENT_TYPES, default='ranking', verbose_name="Tipo")
    competition_type = models.CharField(max_length=20, choices=COMPETITION_TYPES, default='simples', verbose_name="Competição")
    set_format = models.CharField(max_length=20, choices=SET_FORMATS, default='3_normal', verbose_name="Formato de Sets")
    
    current_round = models.IntegerField(verbose_name="Rodada Atual", default=1)
    start_date = models.DateField(verbose_name="Data de Início", null=True, blank=True)
    end_date = models.DateField(verbose_name="Data de Fim", null=True, blank=True)
    number_of_brackets = models.IntegerField(default=1, verbose_name="Número de Chaves (Eliminatório)")
    is_active = models.BooleanField(default=True, verbose_name="Ativo (Exibir no site)")
    is_finished = models.BooleanField(default=False, verbose_name="Encerrado")
    
    points_winner_2x0 = models.IntegerField(null=True, blank=True, default=3, verbose_name="Pontos (Vitória 2x0)")
    points_winner_2x1 = models.IntegerField(null=True, blank=True, default=2, verbose_name="Pontos (Vitória 2x1)")
    points_loser_2x1  = models.IntegerField(null=True, blank=True, default=1, verbose_name="Pontos (Derrota 2x1)")
    points_loser_2x0  = models.IntegerField(null=True, blank=True, default=0, verbose_name="Pontos (Derrota 2x0)")

    # Pontuação por Fase (Torneio Eliminatório — opcional, deixe em branco para não usar)
    pts_round64_participant = models.IntegerField(null=True, blank=True, verbose_name="Round 64 — Pts por Participação")
    pts_round64_winner      = models.IntegerField(null=True, blank=True, verbose_name="Round 64 — Pts por Vitória")
    pts_round32_participant = models.IntegerField(null=True, blank=True, verbose_name="Round 32 — Pts por Participação")
    pts_round32_winner      = models.IntegerField(null=True, blank=True, verbose_name="Round 32 — Pts por Vitória")
    pts_round16_participant = models.IntegerField(null=True, blank=True, verbose_name="Round 16 — Pts por Participação")
    pts_round16_winner      = models.IntegerField(null=True, blank=True, verbose_name="Round 16 — Pts por Vitória")
    pts_oitavas_participant = models.IntegerField(null=True, blank=True, verbose_name="Oitavas — Pts por Participação")
    pts_oitavas_winner      = models.IntegerField(null=True, blank=True, verbose_name="Oitavas — Pts por Vitória")
    pts_quartas_participant = models.IntegerField(null=True, blank=True, verbose_name="Quartas — Pts por Participação")
    pts_quartas_winner      = models.IntegerField(null=True, blank=True, verbose_name="Quartas — Pts por Vitória")
    pts_semi_participant    = models.IntegerField(null=True, blank=True, verbose_name="Semifinal — Pts por Participação")
    pts_semi_winner         = models.IntegerField(null=True, blank=True, verbose_name="Semifinal — Pts por Vitória")
    pts_final_participant   = models.IntegerField(null=True, blank=True, verbose_name="Final — Pts por Participação (Vice)")
    pts_final_winner        = models.IntegerField(null=True, blank=True, verbose_name="Final — Pts por Vitória (Campeão)")
    pts_campeon             = models.IntegerField(null=True, blank=True, verbose_name="Campeão — Pts Extras")

    def __str__(self):
        return f"{self.name} - {self.club.name}"
        
    class Meta:
        verbose_name = "Torneio/Ranking Base"
        verbose_name_plural = "Torneios/Rankings Base"

class RankingTournament(Tournament):
    class Meta:
        proxy = True
        verbose_name = "Ranking"
        verbose_name_plural = "Rankings"

class KnockoutTournament(Tournament):
    class Meta:
        proxy = True
        verbose_name = "Torneio Eliminatório"
        verbose_name_plural = "Torneios Eliminatórios"

class Category(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    is_finished = models.BooleanField(default=False, verbose_name="Encerrada")

    def __str__(self):
        return f"{self.tournament.name} - {self.name}"

    def recalculate_points(self):
        # Zera tudo
        for cp in self.players.all():
            cp.points = 0
            cp.matches_played = 0
            cp.wins = 0
            cp.losses = 0
            cp.save()
            
        # Recalcula baseado nas partidas finalizadas
        for match in self.matches.filter(status='completed'):
            cpa = self.players.filter(player=match.player_a).first()
            cpb = self.players.filter(player=match.player_b).first()
            if cpa and cpb and match.winner:
                cpa.matches_played += 1
                cpb.matches_played += 1
                
                if match.winner == match.player_a:
                    cpa.wins += 1
                    cpb.losses += 1
                    if match.sets_b == 0:
                        cpa.points += self.tournament.points_winner_2x0
                        cpb.points += self.tournament.points_loser_2x0
                    else:
                        cpa.points += self.tournament.points_winner_2x1
                        cpb.points += self.tournament.points_loser_2x1
                elif match.winner == match.player_b:
                    cpb.wins += 1
                    cpa.losses += 1
                    if match.sets_a == 0:
                        cpb.points += self.tournament.points_winner_2x0
                        cpa.points += self.tournament.points_loser_2x0
                    else:
                        cpb.points += self.tournament.points_winner_2x1
                        cpa.points += self.tournament.points_loser_2x1
                cpa.save()
                cpb.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sincroniza o status do Torneio se todas as categorias estiverem encerradas
        tournament = self.tournament
        if tournament.categories.exists() and not tournament.categories.filter(is_finished=False).exists():
            if not tournament.is_finished:
                tournament.is_finished = True
                tournament.save(update_fields=['is_finished'])
        elif tournament.categories.filter(is_finished=False).exists():
            if tournament.is_finished:
                tournament.is_finished = False
                tournament.save(update_fields=['is_finished'])

    class Meta:
        unique_together = ('tournament', 'name')
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

class CategoryPlayer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    points = models.IntegerField(default=0, verbose_name="Pontos")
    matches_played = models.IntegerField(default=0, verbose_name="Jogos")
    wins = models.IntegerField(default=0, verbose_name="Vitórias")
    losses = models.IntegerField(default=0, verbose_name="Derrotas")
    is_seed = models.BooleanField(default=False, verbose_name="Cabeça de Chave")
    seed_number = models.IntegerField(null=True, blank=True, verbose_name="Nº Cabeça de Chave")

    def __str__(self):
        return f"{self.player.name} - {self.category.name}"

    class Meta:
        unique_together = ('category', 'player')
        verbose_name = "Inscrição na Competição"
        verbose_name_plural = "Inscrições nas Competições"
        ordering = ['-points', '-wins', 'matches_played']

class Match(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Finalizado'),
        ('cancelled', 'Não Ocorreu (Cancelado)'),
    ]

    RESULT_STATUS_CHOICES = [
        ('unreported', 'Não Lançado'),
        ('pending_approval', 'Aguardando Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='all_matches', null=True, blank=True)
    round_number = models.IntegerField(verbose_name="Rodada")
    player_a = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_as_a', null=True, blank=True)
    player_b = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_as_b', null=True, blank=True)
    
    SCHEDULE_STATUS_CHOICES = [
        ('unagendado', 'Não Agendado'),
        ('aguardando_adversario', 'Aguardando Adversário'),
        ('agendado', 'Agendado'),
    ]
    schedule_status = models.CharField(max_length=30, choices=SCHEDULE_STATUS_CHOICES, default='unagendado')
    proposed_datetime = models.DateTimeField(null=True, blank=True)
    proposed_court = models.ForeignKey('clubs.Court', on_delete=models.SET_NULL, null=True, blank=True, related_name='proposed_matches')
    proposed_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='proposed_schedules')
    # Workflow de lançamento de resultados
    result_status = models.CharField(max_length=20, choices=RESULT_STATUS_CHOICES, default='unreported')
    reported_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_results')
    proposed_result_json = models.JSONField(null=True, blank=True, verbose_name="Resultado Proposto")
    
    sets_a = models.IntegerField(null=True, blank=True, verbose_name="Sets Ganhos (A)")
    sets_b = models.IntegerField(null=True, blank=True, verbose_name="Sets Ganhos (B)")
    
    set1_a = models.IntegerField(null=True, blank=True, verbose_name="Set 1 (A)")
    set1_b = models.IntegerField(null=True, blank=True, verbose_name="Set 1 (B)")
    set2_a = models.IntegerField(null=True, blank=True, verbose_name="Set 2 (A)")
    set2_b = models.IntegerField(null=True, blank=True, verbose_name="Set 2 (B)")
    set3_a = models.IntegerField(null=True, blank=True, verbose_name="Set 3 (A)")
    set3_b = models.IntegerField(null=True, blank=True, verbose_name="Set 3 (B)")
    set4_a = models.IntegerField(null=True, blank=True, verbose_name="Set 4 (A)")
    set4_b = models.IntegerField(null=True, blank=True, verbose_name="Set 4 (B)")
    set5_a = models.IntegerField(null=True, blank=True, verbose_name="Set 5 (A)")
    set5_b = models.IntegerField(null=True, blank=True, verbose_name="Set 5 (B)")
    
    court = models.ForeignKey('clubs.Court', on_delete=models.SET_NULL, null=True, blank=True, related_name='matches', verbose_name="Quadra Reservada")
    scheduled_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Data e Hora Agendada")
    
    next_match = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_matches')
    phase = models.CharField(max_length=50, blank=True, verbose_name="Fase")
    position_in_bracket = models.IntegerField(null=True, blank=True)
    is_bye = models.BooleanField(default=False, verbose_name="Jogo BYE (Avanço Automático)")
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        pa = self.player_a.name if self.player_a else "TBD"
        pb = self.player_b.name if self.player_b else "TBD"
        return f"{pa} vs {pb}"

    def save(self, *args, **kwargs):
        # Auto-calcula sets_a e sets_b com base nos games, se preenchidos
        has_games = any(v is not None for v in [
            self.set1_a, self.set1_b, self.set2_a, self.set2_b,
            self.set3_a, self.set3_b, self.set4_a, self.set4_b,
            self.set5_a, self.set5_b
        ])
        
        sa = self.sets_a or 0
        sb = self.sets_b or 0
        
        if has_games:
            sa = 0
            sb = 0
            sets = [
                (self.set1_a, self.set1_b),
                (self.set2_a, self.set2_b),
                (self.set3_a, self.set3_b),
                (self.set4_a, self.set4_b),
                (self.set5_a, self.set5_b),
            ]
            for ga, gb in sets:
                if ga is not None and gb is not None:
                    if ga > gb: sa += 1
                    elif gb > ga: sb += 1
            
            self.sets_a = sa
            self.sets_b = sb
            
        # Lógica Automática de Status e Vencedor baseada no Formato do Torneio
        if self.tournament and not self.is_bye:
            sets_to_win = 3 if self.tournament.set_format == '5_normal' else 2
            
            if sa >= sets_to_win or sb >= sets_to_win:
                self.status = 'completed'
                self.winner = self.player_a if sa > sb else self.player_b
            elif self.status != 'cancelled':
                self.status = 'pending'
                self.winner = None
                    
        super().save(*args, **kwargs)

from django.db.models.signals import post_delete

@receiver(post_save, sender=Match)
@receiver(post_delete, sender=Match)
def update_category_points(sender, instance, **kwargs):
    try:
        if getattr(instance, 'category_id', None):
            instance.category.recalculate_points()
    except Exception:
        pass

@receiver(post_save, sender=Match)
def auto_advance_bracket_winner(sender, instance, created, **kwargs):
    """Quando um jogo do bracket é finalizado, avança o vencedor para a próxima fase automaticamente."""
    if instance.status == 'completed' and instance.winner and instance.next_match and instance.position_in_bracket is not None:
        next_m = instance.next_match
        pos = instance.position_in_bracket
        if pos % 2 != 0:  # Ímpar vai para player_a
            if next_m.player_a_id != instance.winner_id:
                Match.objects.filter(pk=next_m.pk).update(player_a=instance.winner)
        else:             # Par vai para player_b
            if next_m.player_b_id != instance.winner_id:
                Match.objects.filter(pk=next_m.pk).update(player_b=instance.winner)
