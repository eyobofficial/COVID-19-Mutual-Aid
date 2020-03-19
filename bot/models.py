from datetime import timedelta

from django.db import models
from django.utils import timezone


class TelegramUser(models.Model):
    """
    Telegram user
    """
    id = models.BigIntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=120, blank=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    is_bot = models.BooleanField(default=False)
    is_manually_added = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at', )

    def __str__(self):
        return self.first_name
