from django.contrib import admin
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import News
from clubs.models import Club


class NewsAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(), label="Conteudo da Noticia")

    class Meta:
        model = News
        fields = "__all__"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ("title", "club_display", "author", "is_published", "published_at", "duplicate_button")
    list_filter = ("is_published", "club")
    search_fields = ("title", "author", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("published_at", "created_at", "updated_at")
    save_on_top = True

    def club_display(self, obj):
        if obj.is_global:
            return "Home do AllCourts365"
        return obj.club if obj.club else "-"
    club_display.short_description = "Clube / Liga"

    def duplicate_button(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        url = reverse('admin:news_news_add') + f'?duplicate={obj.pk}'
        return format_html('<a class="button" style="background-color: #417690; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;" href="{}">Duplicar</a>', url)
    duplicate_button.short_description = "Ações"
    duplicate_button.allow_tags = True

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        duplicate_id = request.GET.get('duplicate')
        if duplicate_id:
            try:
                original = News.objects.get(pk=duplicate_id)
                initial['title'] = f"{original.title} (Cópia)"
                initial['subtitle'] = original.subtitle
                initial['is_global'] = original.is_global
                initial['club'] = original.club_id
                initial['author'] = original.author
                initial['content'] = original.content
                initial['media_credit'] = original.media_credit
                # initial['image'] e 'video' não podem ser clonados trivialmente sem re-upload via admin, mas o texto e config vai todo!
            except News.DoesNotExist:
                pass
        return initial

    fieldsets = (
        ("Identificacao", {
            "fields": ("title", "subtitle", "slug", "is_global", "club")
        }),
        ("Redacao", {
            "fields": ("author", "content")
        }),
        ("Midia Principal", {
            "fields": ("image", "video", "media_credit"),
            "description": "Imagem ou video de destaque da noticia. Preencha o campo de credito/legenda."
        }),
        ("Publicacao", {
            "fields": ("is_published", "published_at", "created_at", "updated_at")
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            # Create a new fieldsets list to avoid modifying the class attribute
            new_fieldsets = []
            for name, opts in fieldsets:
                new_opts = opts.copy()
                if 'fields' in new_opts:
                    fields = list(new_opts['fields'])
                    if 'is_global' in fields:
                        fields.remove('is_global')
                    new_opts['fields'] = tuple(fields)
                new_fieldsets.append((name, new_opts))
            return tuple(new_fieldsets)
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Superuser: ve todos os clubes
        if request.user.is_superuser:
            form.base_fields["club"].queryset = Club.objects.all().order_by("name")
            form.base_fields["club"].required = False
        else:
            # Admin do clube: so ve o seu clube, campo obrigatorio
            managed = Club.objects.filter(administrators=request.user)
            form.base_fields["club"].queryset = managed
            form.base_fields["club"].required = True
            # Pre-preenche o autor com "Redacao <nome do clube>"
            if not obj and managed.exists():
                club = managed.first()
                form.base_fields["author"].initial = f"Redacao {club.name}"
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Admin do clube so ve as noticias do seu clube
        managed_clubs = Club.objects.filter(administrators=request.user)
        return qs.filter(club__in=managed_clubs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        # Garante autor padrao
        if not obj.author:
            if obj.club:
                obj.author = f"Redacao {obj.club.name}"
            else:
                obj.author = "Redacao AllCourts365"
        super().save_model(request, obj, form, change)

from .models import BroadcastMessage
from core.models import Message
from django.contrib.auth.models import User

@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'club_display', 'sender', 'created_at', 'duplicate_button')
    list_filter = ('is_global', 'club')
    search_fields = ('subject', 'body')
    readonly_fields = ('created_at', 'sender')
    
    def duplicate_button(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        url = reverse('admin:news_broadcastmessage_add') + f'?duplicate={obj.pk}'
        return format_html('<a class="button" style="background-color: #417690; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;" href="{}">Duplicar</a>', url)
    duplicate_button.short_description = "Ações"
    duplicate_button.allow_tags = True

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        duplicate_id = request.GET.get('duplicate')
        if duplicate_id:
            try:
                original = BroadcastMessage.objects.get(pk=duplicate_id)
                initial['subject'] = f"{original.subject} (Cópia)"
                initial['body'] = original.body
                initial['is_global'] = original.is_global
                initial['club'] = original.club_id
            except BroadcastMessage.DoesNotExist:
                pass
        return initial
        
    def club_display(self, obj):
        if obj.is_global:
            return "Global (Todos)"
        return obj.club if obj.club else "-"
    club_display.short_description = "Destino"

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (
                ("Destino", {"fields": ("is_global", "club")}),
                ("Conteúdo", {"fields": ("subject", "body")}),
            )
        return (
            ("Destino", {"fields": ("club",)}),
            ("Conteúdo", {"fields": ("subject", "body")}),
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            if "club" in form.base_fields:
                form.base_fields["club"].queryset = Club.objects.all().order_by("name")
                form.base_fields["club"].required = False
        else:
            managed = Club.objects.filter(administrators=request.user)
            if "club" in form.base_fields:
                form.base_fields["club"].queryset = managed
                form.base_fields["club"].required = True
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        managed_clubs = Club.objects.filter(administrators=request.user)
        return qs.filter(club__in=managed_clubs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.sender = request.user
        super().save_model(request, obj, form, change)
        
        # Disparar mensagens na primeira vez (quando criar)
        if not change:
            if obj.is_global:
                target_users = User.objects.filter(is_active=True).exclude(id=request.user.id)
            elif obj.club:
                # Todos os usuários que tem o jogador vinculado ao clube
                target_users = User.objects.filter(is_active=True, player_profiles__club=obj.club).exclude(id=request.user.id).distinct()
            else:
                target_users = []
            
            # Create signature
            signature = f"\n\n---\nEnviado por: {request.user.get_full_name() or request.user.username}"
            if obj.club:
                signature += f" (Administração - {obj.club.name})"
            else:
                signature += " (Administração - AllCourts365)"

            messages_to_create = []
            for user in target_users:
                messages_to_create.append(Message(
                    sender=request.user,
                    recipient=user,
                    subject=obj.subject,
                    body=obj.body + signature,
                    broadcast=obj
                ))
            
            if messages_to_create:
                Message.objects.bulk_create(messages_to_create)
        else:
            # Se for uma edição, atualiza os textos de todas as mensagens que já foram enviadas
            signature = f"\n\n---\nEnviado por: {request.user.get_full_name() or request.user.username}"
            if obj.club:
                signature += f" (Administração - {obj.club.name})"
            else:
                signature += " (Administração - AllCourts365)"
                
            obj.delivered_messages.update(
                subject=obj.subject,
                body=obj.body + signature
            )
