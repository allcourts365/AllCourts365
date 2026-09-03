from django.contrib import admin, messages
from .models import Club, Player, Tournament, RankingTournament, KnockoutTournament, Category, CategoryPlayer, Match
import openpyxl

from django import forms

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
class ClubAdmin(admin.ModelAdmin):
    form = ClubForm
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'club')
    search_fields = ('name',)
    list_filter = ('club',)

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'club', 'tournament_type', 'is_active', 'is_finished')
    list_filter = ('club', 'tournament_type', 'is_active')
    search_fields = ('name',)
    inlines = [CategoryInline]

class RankingTournamentForm(forms.ModelForm):
    excel_file = forms.FileField(
        required=False, 
        label="Upload Planilha de Atletas (Opcional)", 
        help_text="Formato xlsx. Coluna A: Nome do Atleta, Coluna B: Categoria"
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
        
        excel_file = form.cleaned_data.get('excel_file')
        if excel_file:
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active
                
                players_created = 0
                categories_created = 0
                
                for i, row in enumerate(sheet.iter_rows(values_only=True)):
                    if not row or len(row) < 2:
                        continue
                        
                    player_name = str(row[0]).strip() if row[0] else ""
                    category_name = str(row[1]).strip() if row[1] else ""
                    
                    if not player_name or not category_name:
                        continue
                        
                    # Ignorar cabeçalho provável
                    if i == 0 and player_name.lower() in ['nome', 'atleta', 'jogador', 'nome do atleta']:
                        continue
                        
                    # 1. Categoria
                    category, created = Category.objects.get_or_create(
                        tournament=obj, 
                        name=category_name
                    )
                    if created:
                        categories_created += 1
                        
                    # 2. Atleta (vinculado ao Clube)
                    player, created = Player.objects.get_or_create(
                        club=obj.club,
                        name=player_name
                    )
                    if created:
                        players_created += 1
                        
                    # 3. Inscrição na Categoria
                    CategoryPlayer.objects.get_or_create(
                        category=category,
                        player=player
                    )
                    
                messages.success(request, f"Planilha processada com sucesso: {players_created} novos atletas e {categories_created} novas categorias cadastradas.")
                
            except Exception as e:
                messages.error(request, f"Erro ao processar planilha: {str(e)}")

@admin.register(KnockoutTournament)
class KnockoutTournamentAdmin(TournamentAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tournament_type='knockout')

@admin.register(CategoryPlayer)
class CategoryPlayerAdmin(admin.ModelAdmin):
    list_display = ('player', 'category', 'points', 'matches_played', 'wins', 'losses')
    list_filter = ('category__tournament__club', 'category')
    search_fields = ('player__name',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'category', 'status', 'winner')
    list_filter = ('tournament__club', 'status')
    search_fields = ('player_a__name', 'player_b__name')
