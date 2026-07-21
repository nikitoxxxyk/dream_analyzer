from django.contrib.auth.models import User
from django.db import models
import secrets

class TelegramProfile(models.Model):
    """
    Профиль для связи пользователя сайта с Telegram.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name='ID в Telegram')
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name='Username в Telegram')
    is_bot_active = models.BooleanField(default=False, verbose_name='Бот привязан')
    
    # Токен для безопасной привязки (генерируется при запросе)
    linking_token = models.CharField(max_length=64, blank=True)
    token_expires = models.DateTimeField(null=True, blank=True)
    
    def generate_linking_token(self):
        """Генерирует уникальный токен для привязки, действительный 10 минут."""
        from django.utils import timezone
        from datetime import timedelta
        
        self.linking_token = secrets.token_urlsafe(32)
        self.token_expires = timezone.now() + timedelta(minutes=10)
        self.save()
        return self.linking_token
    
    def is_token_valid(self, token):
        """Проверяет, действителен ли токен."""
        from django.utils import timezone
        return self.linking_token == token and self.token_expires > timezone.now()
    
    def __str__(self):
        return f"{self.user.username} - {self.telegram_id or 'Не привязан'}"

# Сигнал для автоматического создания профиля при регистрации пользователя
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_telegram_profile(sender, instance, created, **kwargs):
    if created:
        TelegramProfile.objects.create(user=instance)
