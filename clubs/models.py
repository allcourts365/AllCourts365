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
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Clube"
        verbose_name_plural = "Clubes"

class Player(models.Model):
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
    
    points_winner_2x0 = models.IntegerField(default=3, verbose_name="Pontos (Vitória 2x0)")
    points_winner_2x1 = models.IntegerField(default=2, verbose_name="Pontos (Vitória 2x1)")
    points_loser_2x1 = models.IntegerField(default=1, verbose_name="Pontos (Derrota 2x1)")
    points_loser_2x0 = models.IntegerField(default=0, verbose_name="Pontos (Derrota 2x0)")

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

    def __str__(self):
        return f"{self.player.name} - {self.category.name}"

    class Meta:
        unique_together = ('category', 'player')
        verbose_name = "Classificação"
        verbose_name_plural = "Classificações"
        ordering = ['-points', '-wins', 'matches_played']

class Match(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Finalizado'),
        ('cancelled', 'Não Ocorreu (Cancelado)'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='all_matches', null=True, blank=True)
    round_number = models.IntegerField(verbose_name="Rodada")
    player_a = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_as_a', null=True, blank=True)
    player_b = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_as_b', null=True, blank=True)
    
    sets_a = models.IntegerField(null=True, blank=True, verbose_name="Sets Ganhos (A)")
    sets_b = models.IntegerField(null=True, blank=True, verbose_name="Sets Ganhos (B)")
    
    next_match = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_matches')
    phase = models.CharField(max_length=50, blank=True, verbose_name="Fase")
    position_in_bracket = models.IntegerField(null=True, blank=True)
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        pa = self.player_a.name if self.player_a else "TBD"
        pb = self.player_b.name if self.player_b else "TBD"
        return f"{pa} vs {pb}"
