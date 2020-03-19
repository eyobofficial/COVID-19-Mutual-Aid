from django.contrib import admin

from .models import Question, Choice, Answer, UserSession


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('number', 'text')
    inlines = [ChoiceInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'text', 'created_at')
    list_filter = ('question', 'created_at')
