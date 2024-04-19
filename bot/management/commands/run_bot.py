from django.core.management.base import BaseCommand
from django.conf import settings
from bot.bot import main

from telebot import TeleBot

# Объявление переменной бота
bot = TeleBot(settings.TOKEN, threaded=False)


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write('Bot has been started successfully')
        main()

