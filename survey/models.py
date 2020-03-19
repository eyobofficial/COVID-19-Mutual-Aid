import uuid

from django.contrib.auth import get_user_model
from django.db import models

from bot.models import TelegramUser as User

from .validators import validate_especial_charachters


class Question(models.Model):
    """
    Survey question.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    number = models.IntegerField(unique=True)
    text = models.TextField(
        'question text',
        validators=[validate_especial_charachters]
    )
    note = models.TextField(
        blank=True,
        validators=[validate_especial_charachters],
        help_text='Any notes/remarks you want to add to the question (optional)'
    )

    class Meta:
        ordering = ('number', )

    def __str__(self):
        return  f'{self.number}. {self.text}'


class Choice(models.Model):
    """
    Question choice.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(
        max_length=255,
        validators=[validate_especial_charachters]
    )

    def __str__(self):
        return f'Choice for {self.question.number}'


class Answer(models.Model):
    """
    User anwers for the questions.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('user', 'question__number')
        default_related_name = 'answers'

    def __str__(self):
        return f'{self.text}'


class UserSession(models.Model):
    """
    Current user question.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='session'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    def __str__(self):
        return f'{self.user} - {self.question.number}'
