import telegram

from django.conf import settings

from survey.models import Answer, UserSession, Question, Answer

from .constants import messages
from .models import TelegramUser as User
from .utilities import is_form_completed


class TelegramBot:
    """
    Telegram Bot Handler.
    """
    COMMANDS = ['start', 'help', 'about', 'result', 'form']

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
        Sends message to a user with telegram_id.

        Args:
            chat_id (int): Telegram chat id
            text (str): Message to send
            keyboard (list): Input keyboard button to display
        """
        reply_markup = telegram.ReplyKeyboardRemove()
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
        Replys back to the user sent who sent the message.

        Args:
            text (str): Message to send
            keyboard (list): Input keyboard button to display
        """
        self.send_message(
            chat_id=self.chat_id,
            text=text,
            keyboard=keyboard
        )

    def process(self, user):
        """
        Dispatchs user messages (commands and texts) to the right method.

        Args:
            user: The telegram user instance of the sender
        """
        self.user = user
        self.session, _ = UserSession.objects.get_or_create(
            user=self.user,
            defaults={'question': Question.objects.order_by('number').first()}
        )
        if self.message.startswith('/'):
            command = self.message.lstrip('/')
            if command not in self.COMMANDS:
               self.reply("I don't know this command.")
               self.help()
            else:
                method = getattr(self, command)
                method()
        else:
            self.get_answer(user)

    def start(self):
        """
        Command to reset & restart survey form.
        """
        self.user.answers.all().delete()
        UserSession.objects.filter(user=self.user).delete()
        question_count = Question.objects.count()
        self.reply(
            f'Hi {self.user.first_name}, '
            f'the form contains a total of {question_count} questions.'
        )
        self.send_question()

    def form(self):
        """
        Continues filling the form.
        """
        if is_form_completed(self.user):
            self.reply('You have already completed filling the form.')
            self.result()
        else:
            self.send_question()

    def send_question(self):
        """
        Sends a question and set the current question session.
        """
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
        self.reply(
            f'{self.session.question.number}. {self.session.question.text}',
            keyboard=keyboard
        )

    def get_answer(self, user):
        """
        Handles the user response messages for the current question session.
        """
        if self.session:
            Answer.objects.update_or_create(
                user=self.user,
                question=self.session.question,
                defaults={'text': self.message}
            )
            next_question = Question.objects.filter(
                number__gt=self.session.question.number
            ).first()
            if next_question is None:
                self.reply(
                    f'{self.user.first_name},\n'
                    'Thank you for completing the form. '
                    'Here is what you have filled.\n\n'
                )
                self.result()
            else:
                self.user.session.question = next_question
                self.user.session.save()
                self.send_question()
        else:
            self.start()

    def result(self):
        if not is_form_completed(self.user):
            self.reply('Please complete filling the form first.')
            self.start()
        else:
            answers = Answer.objects.filter(
                user=self.user
            ).order_by('question__number')
            answer_list = []
            for answer in answers:
                line = (
                    f'{answer.question.number}. {answer.question.text}\n'
                    f'`{answer.text}`'
                )
                answer_list.append(line)

            self.reply('\n\n'.join(answer_list))
            self.reply(
                'If you want to change your answer, use the /start command.'
            )

    def help(self, **kwargs):
        """
        Send help message
        """
        self.reply(text=messages.help_message)

    def about(self, **kwargs):
        """
        Send a reply with a brief introduction of the bot.
        """
        self.reply(messages.about_message)
