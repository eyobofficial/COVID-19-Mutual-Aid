import telegram

from django.conf import settings

from survey.models import Answer, UserSession, Question, Answer

from .constants import messages
from .models import TelegramUser as User


class TelegramBot:
    """
    Telegram Bot Handler.
    """
    COMMANDS = ['language', 'form', 'start', 'help', 'welcome']

    def __init__(self, context, **kwargs):
        self.bot = telegram.Bot(settings.TELEGRAM_BOT_TOKEN)
        self.data = context.get('message') or context.get('edited_message')
        self.user = None
        self.session = None

    @property
    def message(self):
        if self.data is not None:
            return self.data['text'].strip()
        return

    @property
    def sender(self):
        if self.data is not None:
            return self.data['from']
        return

    @property
    def chat_id(self):
        if self.data is not None:
            return self.data['chat']['id']
        return

    def send_message(self, chat_id, text, keyboard=None):
        """
        Send message to a user with his/her telegram_id.
        """
        reply_markup = None
        if keyboard:
            reply_markup = telegram.ReplyKeyboardMarkup(
                keyboard,
                on_time_keyboard=True,
                resize_keyboard=True
            )

        self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    def reply(self, text, keyboard=None):
        """
        Reply to the user sent who sent the message.
        """
        if keyboard is not None:
            self.send_message(
                chat_id=self.chat_id,
                text=text,
                keyboard=keyboard
            )
        else:
            reply_markup = telegram.ReplyKeyboardRemove()
            self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

    def process(self, user):
        """
        Dispatch user messages (commands and texts) to the right method.
        """
        self.user = user
        self.session, _ = UserSession.objects.get_or_create(
            user=self.user,
            defaults={'question': Question.objects.order_by('number').first()}
        )
        if self.message.startswith('/'):
            command = self.message.lstrip('/')
            if command not in self.COMMANDS:
               self.reply(
                   "I don't know this command. "
                    "Use /help to see the commands."
                )
            else:
                method = getattr(self, command)
                method()
        else:
            self.get_answer(user)

    def start(self):
        self.user.answers.all().delete()
        UserSession.objects.filter(user=self.user).delete()
        self.send_question()

    def send_question(self):
        keyboard = None
        self.session, _ = UserSession.objects.get_or_create(
            user=self.user,
            defaults={
                'question': Question.objects.order_by('number').first()
            }
        )
        choice_list = self.session.question.choices.all()
        if choice_list.count():
            keyboard = [[choice.text] for choice in choice_list]
        self.reply(text=self.session.question.text, keyboard=keyboard)

    def get_answer(self, user):
        """
        Handle the user response messages.
        """
        if self.session:
            Answer.objects.update_or_create(
                user=self.user,
                question=self.session.question,
                answer=self.message
            )
            next_question = Question.objects.filter(
                number__gt=self.session.question.number
            ).first()
            if next_question is None:
                self.result()
            else:
                self.user.session.question = next_question
                self.user.session.save()
                self.send_question()
        else:
            self.start()

    def result(self):
        self.reply('Summary goes here')

    def help(self, **kwargs):
        """
        Send help message
        """
        self.reply(text=messages.help_message)

    def about(self, **kwargs):
        """
        Send a reply with a brief introduction of the bot.
        """
        self.reply(text=messages.about)
