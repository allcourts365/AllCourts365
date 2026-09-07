from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField


class News(models.Model):
    # Identificacao
    title = models.CharField(max_length=300, verbose_name="Titulo")
    subtitle = models.CharField(max_length=500, blank=True, verbose_name="Subtitulo")
    slug = models.SlugField(max_length=350, unique=True, blank=True, verbose_name="Slug (URL)")

    # Vinculo
    is_global = models.BooleanField(
        default=False,
        verbose_name="Home do AllCourts365",
        help_text="Marque para veicular esta noticia na home global."
    )
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news',
        verbose_name="Clube / Liga",
        help_text="Clube ou liga a qual a noticia pertence."
    )

    # Conteudo
    author = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Escrito por",
        help_text="Ex: Redacao AllCourts365 ou Redacao Clube 22 de Agosto"
    )
    content = RichTextUploadingField(verbose_name="Conteudo da Noticia")

    # Midia principal
    image = models.ImageField(upload_to='news/images/', null=True, blank=True, verbose_name="Imagem de Destaque")
    video = models.FileField(upload_to='news/videos/', null=True, blank=True, verbose_name="Video de Destaque")
    media_credit = models.CharField(
        max_length=400,
        blank=True,
        verbose_name="Credito / Legenda da Midia",
        help_text="Ex: Foto: Joao Silva | Arquivo do clube"
    )

    # Publicacao
    is_published = models.BooleanField(default=False, verbose_name="Publicado")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de Publicacao")

    # Metadados
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='news_created', verbose_name="Criado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    # Curtidas
    likes = models.ManyToManyField(User, related_name='news_likes', blank=True, verbose_name="Curtidas")
    anonymous_likes = models.PositiveIntegerField(default=0, verbose_name="Curtidas Anonimas")

    class Meta:
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        club_name = self.club.name if self.club else "AllCourts365"
        return f"[{club_name}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        # Default author
        if not self.author:
            if self.club:
                self.author = f"Redacao {self.club.name}"
            else:
                self.author = "Redacao AllCourts365"

        super().save(*args, **kwargs)

    @property
    def display_author(self):
        return self.author or ("Redacao " + (self.club.name if self.club else "AllCourts365"))

    @property
    def get_total_likes(self):
        return self.likes.count() + self.anonymous_likes
