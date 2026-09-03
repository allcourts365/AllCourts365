from django.contrib import admin, messages
from .models import Club, Player, Tournament, RankingTournament, KnockoutTournament, Category, CategoryPlayer, Match
import openpyxl

from django import forms
from django.utils.safestring import mark_safe

class ClubScopedAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        model_name = self.model.__name__
        if model_name == 'Club':
            return qs.filter(administrators=request.user).distinct()
        elif model_name in ['Player', 'Tournament', 'RankingTournament', 'KnockoutTournament']:
            return qs.filter(club__administrators=request.user).distinct()
        elif model_name in ['Category', 'Match']:
            return qs.filter(tournament__club__administrators=request.user).distinct()
        elif model_name == 'CategoryPlayer':
            return qs.filter(category__tournament__club__administrators=request.user).distinct()
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "club":
                kwargs["queryset"] = Club.objects.filter(administrators=request.user)
            elif db_field.name == "tournament":
                kwargs["queryset"] = Tournament.objects.filter(club__administrators=request.user)
            elif db_field.name == "category":
                kwargs["queryset"] = Category.objects.filter(tournament__club__administrators=request.user)
            elif db_field.name in ["player", "player_a", "player_b", "winner"]:
                kwargs["queryset"] = Player.objects.filter(club__administrators=request.user)
                
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = '__all__'
        widgets = {
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'overlay_color': forms.TextInput(attrs={'type': 'color'}),
            'highlight_color': forms.TextInput(attrs={'type': 'color'}),
            'title_color': forms.TextInput(attrs={'type': 'color'}),
            'subtitle_color': forms.TextInput(attrs={'type': 'color'}),
        }

@admin.register(Club)
class ClubAdmin(ClubScopedAdminMixin, admin.ModelAdmin):
    form = ClubForm
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('administrators',)
    readonly_fields = ('manage_admins_links',)
    
    def manage_admins_links(self, obj):
        from django.utils.html import format_html
        if not obj or not obj.pk:
            return "Salve o clube primeiro para gerenciar seus administradores."
        
        links = []
        for admin_user in obj.administrators.all():
            url = f"/admin/auth/user/{admin_user.pk}/change/"
            links.append(f'<a href="{url}" target="_blank" class="button" style="margin-bottom:5px;">✏️ Editar / Mudar Senha de <strong>{admin_user.username}</strong></a>')
        
        if not links:
            return "Nenhum administrador vinculado ainda."
            
        return format_html("<br><br>".join(links))
    manage_admins_links.short_description = "Ajustar Senhas / Usuários"

@admin.register(Player)
class PlayerAdmin(ClubScopedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'club')
    search_fields = ('name',)
    list_filter = ('club',)

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1

@admin.register(Tournament)
class TournamentAdmin(ClubScopedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'club', 'tournament_type', 'is_active', 'is_finished')
    list_filter = ('club', 'tournament_type', 'is_active')
    search_fields = ('name',)
    inlines = [CategoryInline]

class RankingTournamentForm(forms.ModelForm):
    excel_file = forms.FileField(
        required=False, 
        label="Upload Planilha de Sorteio Automático", 
        help_text=mark_safe('Formato xlsx. Coluna A: Nome do Atleta, Coluna B: Categoria. <br><a href="/static/planilha_exemplo.xlsx" download>📥 Baixar planilha de sorteio</a>')
    )
    
    history_file = forms.FileField(
        required=False,
        label="Upload Planilha de Histórico (Jogos já realizados)",
        help_text=mark_safe('Formato xlsx. Colunas: A(Atleta A), B(Atleta B), C(Sets A), D(Sets B), E(Categoria), F(Rodada), G(Status). <br><a href="/static/planilha_historico.xlsx" download>📥 Baixar planilha de histórico</a>')
    )
    
    class Meta:
        model = RankingTournament
        fields = '__all__'

@admin.register(RankingTournament)
class RankingTournamentAdmin(TournamentAdmin):
    form = RankingTournamentForm

    def get_queryset(self, request):
        return super().get_queryset(request).filter(tournament_type='ranking')
        
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # 1. PROCESSAR SORTEIO AUTOMÁTICO
        excel_file = form.cleaned_data.get('excel_file')
        if excel_file:
            self._process_draw_upload(request, obj, excel_file)
            
        # 2. PROCESSAR HISTÓRICO DE JOGOS
        history_file = form.cleaned_data.get('history_file')
        if history_file:
            self._process_history_upload(request, obj, history_file)

    def _process_draw_upload(self, request, obj, excel_file):
        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            categories_affected = set()
            
            for i, row in enumerate(sheet.iter_rows(values_only=True)):
                if not row or len(row) < 2:
                    continue
                    
                player_name = str(row[0]).strip() if row[0] else ""
                category_name = str(row[1]).strip() if row[1] else ""
                
                if not player_name or not category_name:
                    continue
                    
                if i == 0 and player_name.lower() in ['nome', 'atleta', 'jogador', 'nome do atleta']:
                    continue
                    
                category, _ = Category.objects.get_or_create(tournament=obj, name=category_name)
                categories_affected.add(category)
                
                player, _ = Player.objects.get_or_create(club=obj.club, name=player_name)
                CategoryPlayer.objects.get_or_create(category=category, player=player)
                
            matches_created = 0
            
            for category in categories_affected:
                if Match.objects.filter(category=category, status='completed').exists():
                    messages.warning(request, f"Categoria '{category.name}' ignorada para sorteio: já possui jogos finalizados.")
                    continue
                
                Match.objects.filter(category=category, status='pending').delete()
                
                players = list(Player.objects.filter(categoryplayer__category=category))
                if len(players) < 2:
                    continue
                    
                if len(players) % 2 != 0:
                    players.append(None) # None representará o "Bye/Folga"
                    
                n = len(players)
                rounds = n - 1
                
                for r in range(rounds):
                    for i in range(n // 2):
                        p1 = players[i]
                        p2 = players[n - 1 - i]
                        
                        if p1 is not None and p2 is not None:
                            Match.objects.create(
                                category=category,
                                tournament=obj,
                                round_number=r + 1,
                                player_a=p1,
                                player_b=p2,
                                status='pending'
                            )
                            matches_created += 1
                    
                    players = [players[0]] + [players[-1]] + players[1:-1]
                    
            messages.success(request, f"Sorteio realizado: {matches_created} partidas pendentes geradas.")
            
        except Exception as e:
            messages.error(request, f"Erro ao processar planilha de sorteio: {str(e)}")

    def _process_history_upload(self, request, obj, history_file):
        try:
            wb = openpyxl.load_workbook(history_file)
            sheet = wb.active
            
            matches_imported = 0
            
            for i, row in enumerate(sheet.iter_rows(values_only=True)):
                if not row or len(row) < 6:
                    continue
                    
                player_a_name = str(row[0]).strip() if row[0] else ""
                player_b_name = str(row[1]).strip() if row[1] else ""
                
                if not player_a_name or not player_b_name:
                    continue
                    
                if i == 0 and player_a_name.lower() in ['atleta a', 'jogador a']:
                    continue
                
                try:
                    sets_a = int(row[2]) if row[2] is not None else 0
                    sets_b = int(row[3]) if row[3] is not None else 0
                    category_name = str(row[4]).strip() if row[4] else "Única"
                    round_number = int(row[5]) if row[5] is not None else 1
                    status_raw = str(row[6]).strip().lower() if len(row) > 6 and row[6] is not None else "finalizado"
                except ValueError:
                    continue
                    
                match_status = 'pending' if status_raw in ['pendente', 'pending', 'aguardando'] else 'completed'
                
                category, _ = Category.objects.get_or_create(tournament=obj, name=category_name)
                
                pa, _ = Player.objects.get_or_create(club=obj.club, name=player_a_name)
                pb, _ = Player.objects.get_or_create(club=obj.club, name=player_b_name)
                
                cpa, _ = CategoryPlayer.objects.get_or_create(category=category, player=pa)
                cpb, _ = CategoryPlayer.objects.get_or_create(category=category, player=pb)
                
                winner = None
                if match_status == 'completed':
                    if sets_a > sets_b:
                        winner = pa
                    elif sets_b > sets_a:
                        winner = pb
                    
                Match.objects.create(
                    category=category,
                    tournament=obj,
                    round_number=round_number,
                    player_a=pa,
                    player_b=pb,
                    sets_a=sets_a if match_status == 'completed' else None,
                    sets_b=sets_b if match_status == 'completed' else None,
                    winner=winner,
                    status=match_status
                )
                
                matches_imported += 1
                
                # Atualiza pontos apenas se o jogo foi finalizado
                if match_status == 'completed':
                    if winner == pa:
                        if sets_b == 0:
                            cpa.points += obj.points_winner_2x0
                            cpb.points += obj.points_loser_2x0
                        else:
                            cpa.points += obj.points_winner_2x1
                            cpb.points += obj.points_loser_2x1
                        cpa.wins += 1
                        cpb.losses += 1
                    elif winner == pb:
                        if sets_a == 0:
                            cpb.points += obj.points_winner_2x0
                            cpa.points += obj.points_loser_2x0
                        else:
                            cpb.points += obj.points_winner_2x1
                            cpa.points += obj.points_loser_2x1
                        cpb.wins += 1
                        cpa.losses += 1
                        
                    cpa.matches_played += 1
                    cpb.matches_played += 1
                    cpa.save()
                    cpb.save()
                
            messages.success(request, f"Histórico importado: {matches_imported} partidas processadas com sucesso.")
            
        except Exception as e:
            messages.error(request, f"Erro ao processar planilha de histórico: {str(e)}")

@admin.register(KnockoutTournament)
class KnockoutTournamentAdmin(TournamentAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tournament_type='knockout')

@admin.register(CategoryPlayer)
class CategoryPlayerAdmin(ClubScopedAdminMixin, admin.ModelAdmin):
    list_display = ('player', 'category', 'points', 'matches_played', 'wins', 'losses')
    list_filter = ('category__tournament__club', 'category')
    search_fields = ('player__name',)

@admin.register(Match)
class MatchAdmin(ClubScopedAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'round_number', 'tournament', 'category', 'status', 'winner')
    list_filter = ('tournament__club', 'tournament', 'category', 'round_number', 'status')
    search_fields = ('player_a__name', 'player_b__name')
