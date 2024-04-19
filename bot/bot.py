import time

from django.conf import settings

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from .models import User, Question, Animal, Review


# Объявление переменной бота
bot = TeleBot(settings.TOKEN, threaded=False)

# словарь выбранных пользователем ответов result[chat_id]=[answer1, answer2]
result = {}

# словарь животных, соответствующих выбранным ответам animal_result[chat_id]=[animal1, animal2]
animal_result = {}


# получение состояние пользователя
def get_user_state(chat_id):
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        return user.state


# обновление состояние пользователя
def update_user_state(chat_id, new_state):
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        user.state = new_state
        user.save()


# стартовое сообщение - создание пользователя, подводка к тесту
@bot.message_handler(commands=['start'])
def handle_start(message):
    user, created = User.objects.get_or_create(
        chat_id=message.chat.id,
        username=message.chat.username,
        state=1,
    )

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = KeyboardButton('\U0001F43E Тест')
    start_staff_button = KeyboardButton('\U0001F43C Написать сотруднику зоопарка')
    markup.add(start_button, start_staff_button)

    start_image = open('media/images/start_message.png', 'rb')
    start_message = f'Добро пожаловать, {user.username}! \n\n\U0001F331 Нажми на Тест в меню, чтобы узнать, какое ' \
                    f'твое тотемное животное в Московском зоопарке'

    bot.send_photo(message.chat.id, start_image, caption=start_message, reply_markup=markup)


# обработчик и сохранение отзыва от пользователя
@bot.message_handler(func=lambda message: message.text.startswith('Отзыв:'))
def create_review(message):
    chat_id = message.chat.id
    user = User.objects.filter(chat_id=chat_id).first()
    username = user.username
    text = message.text.replace('Отзыв:', '')
    Review.objects.create(chat_id=chat_id, username=username, review_text=text)
    bot.send_message(chat_id, 'Спасибо! Ваш отзыв сохранен \U0001F49A')


# запуск теста, обработка start и result кнопок
@bot.message_handler(content_types=['text'])
def message_handler(message):
    chat_id = message.chat.id
    result[chat_id] = []
    user = User.objects.filter(chat_id=chat_id).first()

    if message.text == '\U0001F43E Тест':
        phone_gif = open('media/images/rotate_phone.gif', 'rb')
        phone_message = f'Переверните телефон для прохождения теста'
        bot.send_animation(chat_id, phone_gif, caption=phone_message)
        time.sleep(3)
        ask_next_question(message.chat.id)

    elif message.text == '\U0001F999 Написать сотруднику зоопарка':
        admin_chat_id = 350685069
        admin_message = f'Пользователь @{user.username} хочет связаться с вами.\n\n Результат теста:' \
                        f'\n <b>{user.test_result}</b>'
        bot.send_message(chat_id=admin_chat_id, text=admin_message, parse_mode='HTML')
        bot.send_message(chat_id, f'Перейдите в чат с нашим сотрудником @dashazhu для дальнейшего общения \U0001F43E')

    elif message.text == '\U0001F425 Попробовать еще раз?':
        user.state = 1
        user.save()
        ask_next_question(chat_id)

    elif message.text == '\U0001F43E Оставить отзыв':
        bot_review_message = f'Отправьте свой отзыв в начале написав "Отзыв":\n<b>Отзыв:</b> текст отзыва\n\n' \
                             f'Например,\nОтзыв: я бы хотел быть тигром...'
        bot.send_message(chat_id, bot_review_message, parse_mode='HTML')

    else:
        error_text = f'/start - начало работы бота \n\U0001F43E Тест - начать тест \n\U0001F425 Попробовать еще раз' \
                     f'\n\U0001F999 Написать сотруднику зоопарка \n\U0001F43E Оставить отзыв'
        bot.send_message(chat_id, f'К сожалению, я не понял, что вы написали. Напомню о своих командах:\n\n{error_text}')


# вывод вопросов
def ask_next_question(chat_id):
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        user_state = get_user_state(chat_id=chat_id)
        question = Question.objects.get(order_in_test=user_state)
        bot.send_message(chat_id, f'\U0001F331 Вопрос {question.order_in_test}:\n{question.question}',
                         reply_markup=gen_markup(question.answers))


# кнопки вариантов ответа на вопрос
def gen_markup(answers):
    markup = InlineKeyboardMarkup()
    for answer in answers:
        answer = str(answer)
        markup.add(InlineKeyboardButton(
            f'{answer}', callback_data=answer[0:5]
        ))
    return markup


# обработка ответа на вопрос
@bot.callback_query_handler(func=lambda call: True)
def callback_answers(call):
    chat_id = call.message.chat.id
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        user_state = get_user_state(chat_id)
        question_answers = Question.objects.filter(order_in_test=user_state).values_list('answers', flat=True)
        question_answers = question_answers[0]
        for answer in question_answers:
            if call.data in answer:
                result[chat_id].append(answer)
                if (user_state + 1) > Question.objects.count():
                    get_result(result[chat_id], chat_id)
                else:
                    new_state = user_state + 1
                    update_user_state(chat_id, new_state)
                    ask_next_question(chat_id)


# обработка ответов пользователя: из ответа в животное
def get_result(user_answers, chat_id):
    animal_result[chat_id] = []
    animals = Animal.objects.all().values_list('answers', flat=True)
    for answer in user_answers:
        for animal_answers in animals:
            if answer in animal_answers:
                animal = Animal.objects.filter(answers__contains=[answer]).values('name').first()
                animal_result[chat_id].append(animal['name'])

    calculate_result(chat_id, animal_result[chat_id])


# получение результата теста
def calculate_result(chat_id, result_animal):
    result_markup = ReplyKeyboardMarkup(resize_keyboard=True)

    replay_button = KeyboardButton('\U0001F425 Попробовать еще раз?')
    result_staff_button = KeyboardButton('\U0001F999 Написать сотруднику зоопарка')
    review = KeyboardButton('\U0001F43E Оставить отзыв')

    result_inline = InlineKeyboardMarkup()
    url = f'https://vk.com/share.php?url=https://t.me/moscowzoo_test_bot&comment=Узнай, какое твое тотемное животное ' \
          f'в Московском зоопарке'
    vk_inline_button = InlineKeyboardButton('Поделиться в ВК', url=url)

    result_inline.add(vk_inline_button)
    result_markup.add(replay_button, result_staff_button, review)

    main_result = {an: result_animal.count(an) for an in result_animal}
    max_value = max(main_result.values())
    for key in main_result:
        if main_result[key] == max_value:
            user = User.objects.filter(chat_id=chat_id).first()
            animal = Animal.objects.filter(name=key).first()
            user.test_result = animal
            user.save()
            bot.send_photo(chat_id, animal.animal, caption=f'{animal.test_result}', parse_mode='HTML',
                           reply_markup=result_markup)
            bot.send_message(chat_id, 'Хотите поделиться ботом в ВК?', reply_markup=result_inline)
            break


def main():
    bot.polling(none_stop=True)
