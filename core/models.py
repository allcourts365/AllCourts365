from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class SiteConfiguration(models.Model):
    POSITION_CHOICES = [
        ('top-left', 'Superior Esquerdo'),
        ('top-right', 'Superior Direito'),
        ('bottom-left', 'Inferior Esquerdo'),
        ('bottom-right', 'Inferior Direito'),
        ('center', 'Centro'),
    ]

    # Imagens / Vídeos
    favicon = models.ImageField(upload_to='site_config/favicons/', null=True, blank=True, verbose_name="Favicon", help_text="Imagem que aparece na guia do navegador (recomendado: 32x32 ou 64x64)")
    background_image = models.ImageField(upload_to='site_config/', null=True, blank=True, verbose_name="Imagem de Fundo")
    background_video = models.FileField(upload_to='site_config/videos/', null=True, blank=True, verbose_name="Vídeo de Fundo", help_text="Se preenchido, o vídeo sobrescreve a imagem de fundo. Use arquivos .mp4 ou .webm.")
    watermark_image = models.ImageField(upload_to='site_config/', null=True, blank=True, verbose_name="Marca d'Água")
    
    # Cores (Armazenaremos em Hexadecimal, ex: #FFFFFF)
    background_color = models.CharField(max_length=7, default='#0f172a', verbose_name="Cor de Fundo Fixa")
    overlay_color = models.CharField(max_length=7, default='#000000', verbose_name="Cor do Fumê (Overlay)")
    overlay_opacity = models.FloatField(default=0.5, verbose_name="Opacidade do Fumê (0.0 a 1.0)", help_text="0 = Transparente, 1 = Sólido")
    
    highlight_color = models.CharField(max_length=7, default='#3b82f6', verbose_name="Cor de Destaque (Botões, Links)")
    title_color = models.CharField(max_length=7, default='#ffffff', verbose_name="Cor do Título Principal")
    subtitle_color = models.CharField(max_length=7, default='#94a3b8', verbose_name="Cor do Subtítulo")
    
    # Configurações da Marca d'Água
    watermark_position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='bottom-left', verbose_name="Posição da Marca d'Água")
    watermark_opacity = models.FloatField(default=0.8, verbose_name="Opacidade da Marca d'Água (0.0 a 1.0)")
    watermark_size_percent = models.IntegerField(default=15, verbose_name="Tamanho da Marca d'Água (%)", help_text="Porcentagem em relação à tela")

    # Rodapé (Footer)
    footer_show = models.BooleanField(default=True, verbose_name="Exibir Rodapé (Footer)")
    footer_text = models.TextField(blank=True, verbose_name="Texto/Copyright do Rodapé")
    footer_width = models.CharField(max_length=20, default='100%', verbose_name="Largura do Rodapé", help_text="Ex: 100%, 1200px, 80vw")
    footer_padding = models.CharField(max_length=20, default='40px 20px', verbose_name="Espessura (Padding) do Rodapé", help_text="Ex: 40px 20px (40px em cima/baixo, 20px nas laterais) ou 10px")
    footer_instagram = models.URLField(blank=True, verbose_name="Link do Instagram")
    footer_facebook = models.URLField(blank=True, verbose_name="Link do Facebook")
    footer_whatsapp = models.CharField(max_length=50, blank=True, verbose_name="Número do WhatsApp", help_text="Apenas números, com DDD (ex: 5511999999999)")

    # Monitoramento e SEO
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID de Medição do Google Analytics", help_text="Ex: G-XXXXXXXXXX")
    
    # Recursos e Exibição
    show_clubs_cta = models.BooleanField(default=True, verbose_name="Exibir botão 'Para Clubes' no menu", help_text="Se desmarcado, a opção de prospectar novos clubes não aparecerá no topo do site.")

    @property
    def clean_whatsapp(self):
        if self.footer_whatsapp:
            return ''.join(filter(str.isdigit, self.footer_whatsapp))
        return ''

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configuração do Site"

    def __str__(self):
        return "Configurações Globais do Site"

    def save(self, *args, **kwargs):
        # Implementando o padrão Singleton: garante que só haja 1 registro
        self.pk = 1
        super(SiteConfiguration, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True, verbose_name="Nome Completo")
    racket = models.CharField(max_length=100, blank=True, verbose_name="Raquete que usa")
    handedness = models.CharField(max_length=50, choices=[('D', 'Destro'), ('C', 'Canhoto'), ('A', 'Ambidestro')], blank=True, verbose_name="Empunhadura")
    backhand = models.CharField(max_length=50, choices=[('1', 'Uma Mão'), ('2', 'Duas Mãos')], blank=True, verbose_name="Backhand")

    def __str__(self):
        return f"Perfil de {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)


class PlayerLinkRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='link_requests', verbose_name="Usuário Requerente")
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, verbose_name="Clube")
    player = models.ForeignKey('clubs.Player', on_delete=models.CASCADE, verbose_name="Atleta Desejado")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Resolvido em")

    class Meta:
        verbose_name = "Solicitação de Vínculo de Atleta"
        verbose_name_plural = "Solicitações de Vínculo de Atleta"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} quer ser {self.player.name} no {self.club.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Quando a solicitação for aprovada, vinculamos de fato o Atleta ao Usuário
        if self.status == 'approved':
            self.player.user = self.user
            self.player.save()
        elif self.status in ['pending', 'rejected']:
            if self.player.user == self.user:
                self.player.user = None
                self.player.save()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True, verbose_name="Remetente")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name="Destinatário")
    subject = models.CharField(max_length=200, verbose_name="Assunto")
    body = models.TextField(verbose_name="Mensagem")
    is_read = models.BooleanField(default=False, verbose_name="Lida")
    related_match = models.ForeignKey('clubs.Match', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Jogo Relacionado")
    broadcast = models.ForeignKey('news.BroadcastMessage', on_delete=models.CASCADE, null=True, blank=True, related_name='delivered_messages', verbose_name="Comunicado Origem")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviada em")

    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - para {self.recipient.username}"

from allauth.account.models import EmailAddress


@receiver(post_save, sender=User)
def auto_verify_admin_email(sender, instance, created, **kwargs):
    if instance.is_staff or instance.is_superuser:
        if instance.email:
            email_address, email_created = EmailAddress.objects.get_or_create(
                user=instance,
                email=instance.email,
                defaults={'verified': True, 'primary': True}
            )
            if not email_created and not email_address.verified:
                email_address.verified = True
                email_address.save()

class ClubLead(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome do Responsável")
    club_name = models.CharField(max_length=200, verbose_name="Nome do Clube/Liga")
    phone = models.CharField(max_length=50, verbose_name="WhatsApp/Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail (Opcional)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Solicitação")
    contacted = models.BooleanField(default=False, verbose_name="Contato Realizado?")

    class Meta:
        verbose_name = "Interesse de Clube (Lead)"
        verbose_name_plural = "Interesses de Clubes (Leads)"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.club_name} - {self.name}"
