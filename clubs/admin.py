from django.contrib import admin
from .models import Club, Player, Tournament, RankingTournament, KnockoutTournament, Category, CategoryPlayer, Match

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

@admin.register(RankingTournament)
class RankingTournamentAdmin(TournamentAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tournament_type='ranking')

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
