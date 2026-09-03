from django.db import models

class SiteConfiguration(models.Model):
    POSITION_CHOICES = [
        ('top-left', 'Superior Esquerdo'),
        ('top-right', 'Superior Direito'),
        ('bottom-left', 'Inferior Esquerdo'),
        ('bottom-right', 'Inferior Direito'),
        ('center', 'Centro'),
    ]

    # Imagens
    background_image = models.ImageField(upload_to='site_config/', null=True, blank=True, verbose_name="Imagem de Fundo")
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
