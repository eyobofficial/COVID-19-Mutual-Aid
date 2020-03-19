import telegram

from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from braces.views import CsrfExemptMixin

from rest_framework.authentication import BasicAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .bots import TelegramBot
from .models import TelegramUser as User


@method_decorator(csrf_exempt, name='dispatch')
class TelegramBotView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        context = request.data
        bot = TelegramBot(context)
        user, _ = User.objects.get_or_create(
            id=bot.sender['id'],
            defaults={
                'first_name': bot.sender['first_name'],
                'last_name': bot.sender.get('last_name', ''),
                'username': bot.sender.get('username', ''),
                'is_bot': bot.sender.get('is_bot', False)
            }
        )
        user.access_count += 1
        user.save()
        bot.process(user)
        return Response(status=status.HTTP_200_OK)



