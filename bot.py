from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup
from bs4 import BeautifulSoup
from random import shuffle
import requests


def start(update, context):
    context.chat_data['activity'] = list()
    keyboard = [['Россия', 'США'], ['Мир', 'ТОП-10 стран'], ['Сайт по борьбе с коронавирусом',
                                                             'Случайное развлечение'], ['Новые случаи в России']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('🌍Введите название любой страны, я постараюсь предоставить статистику!\n\n'
                              '🎉 Нажмите на клавиатуре кнопку "Случайное развлечение", если не знаете,'
                              'чем себя занять\n\n', reply_markup=markup)


def message_hand(update, context):
    text = update.message.text.strip().lower()
    if text == 'случайное развлечение':
        update.message.reply_text(activity(context))
        return
    if text == 'топ-10 стран':
        update.message.reply_text(get_top())
        return
    if text == 'новые случаи в россии':
        update.message.reply_text(new_cases())
        return
    if text == 'сайт по борьбе с коронавирусом':
        update.message.reply_text('🦠 стопкоронавирус.рф')
        return
    update.message.reply_text(country_handler(text))


def get_stats(country):
    if country == 'мир':
        url = 'https://www.worldometers.info/coronavirus/'
        style = 'font-size:13px; color:#999; margin-top:5px; text-align:center'
    else:
        url = f'https://www.worldometers.info/coronavirus/country/{country}'
        style = 'font-size:13px; color:#999; text-align:center'

    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')

    if '404 Not Found' in str(soup):
        return '❌ Не удалось получить статистику по указанной стране'

    cases = soup.findAll('div', class_='maincounter-number')

    latest_update = soup.findAll('div', style=style)[0].text
    latest_update = ' '.join(translate(latest_update, lang='en-ru').split()[:-1]) + ' GMT'
    latest_update = latest_update.split(':')
    to_return = f'🟨Всего заболело: {cases[0].text.strip()}\n\n' \
                f'🟥Умерло: {cases[1].text.strip()}\n\n' \
                f'🟩Выздоровело: {cases[2].text.strip()}\n\n' \
                f'{latest_update[0]}:\n' \
                f'{latest_update[1]}:{latest_update[2]}'

    return to_return


def country_handler(country):
    countries = {
        'мир': 'мир',
        'сша': 'us',
        'великобритания': 'uk',
        'россия': 'russia',
        'беларусь': 'belarus',
        'южная корея': 'south-korea',
        'италия': 'italy',
        'испания': 'spain',
        'чехия': 'czech-republic',
        'украина': 'ukraine',
        'казахстан': 'kazakhstan',
        'турция': 'turkey',
        'германия': 'germany',
    }

    if country in countries.keys():
        stats = get_stats(countries[country])

        if country == 'мир':
            message = 'Статистика по всему миру\n\n'
        else:
            message = f'Статистика по стране {country.capitalize() if country != "сша" else country.upper()}\n\n'

        return message + stats

    country_url = translate(country)
    stats = get_stats(country_url)

    return f'Статистика по стране {country.capitalize()}\n\n' + stats


def translate(text, lang='ru-en'):
    yandex_translate_api = 'https://translate.yandex.net/api/v1.5/tr.json/translate'

    params = {
        'key': 'trnsl.1.1.20200330T161011Z.4777f8ad251f2aae.1e137893605996ff5aec1c7f39a813ca10b3bd3a',
        'lang': lang,
        'text': text
    }

    json_response = requests.get(yandex_translate_api, params=params).json()

    return json_response['text'][0].strip()


def get_top():
    # List of countries
    page = requests.get('https://news.google.com/covid19/map?hl=ru&gl=RU&ceid=RU:ru')
    soup = BeautifulSoup(page.text, 'html.parser')
    top = soup.findAll('th', class_='l3HOY')

    result = ['•' + country.text for country in top[1:11]]

    return '😷 ТОП-10 стран 😷\n\n' + '\n'.join(result)


def new_cases():
    page = requests.get('https://www.worldometers.info/coronavirus/country/russia/')

    soup = BeautifulSoup(page.text, 'html.parser')

    cases = soup.findAll('li', class_='news_li')[0].text.split()

    new_cases_ = 'Новых случаев: ' + cases[0] + '\n'
    new_deaths = 'Смертей: ' + cases[4] + '\n'

    return new_cases_ + new_deaths


offers = ['Вот фильмы, которые должени посмотреть каждый!\n'
          'https://www.ivi.ru/titr/goodmovies/30-must-see',
          'Здесь много образовательных курсов: как платных, так и бесплатных\n'
          'https://welcome.stepik.org',
          'Metropolitan Opera анонсировала бесплатные стримы Live in HD.\n'
          'Расписание и ссылки на просмотр здесь:\n'
          'https://www.metopera.org/user-information/nightly-met-opera-streams/',
          'Туринский «Ювентус» открыл болельщикам бесплатный доступ к клубному телевидению.\n'
          'https://www.juventus.com/it/',
          'Пятичасовое путешествие по Эрмитажу, снятое на iPhone 11 Pro одним дублем в 4К\n'
          'https://www.youtube.com/watch?v=_MU73rsL9qE',
          'Образовательная онлайн-платформа «Учи.ру» с 23 марта дает возможность проводить'
          ' уроки во время карантина по видеосвязи.\n'
          'https://lp.uchi.ru/distant-uchi',
          'Курс по инвестициям Тинькофф-журнала.\n'
          'https://journal.tinkoff.ru/pro/invest/#/',
          'Музыкальная платформа Boiler Room запустит онлайн-кинофестиваль The 4:3.'
          ' С 16 апреля по 18 мая она покажет 13 фильмов.'
          ]


def activity(context):
    if not context.chat_data['activity']:
        context.chat_data['activity'] = offers[:]
        shuffle(context.chat_data['activity'])
        action = context.chat_data['activity'][0]

        del context.chat_data['activity'][0]

        return action
    else:
        action = context.chat_data['activity'][0]

        del context.chat_data['activity'][0]

        return action


def main():
    updater = Updater('1273560851:AAHkGnpdZhJ4x0xyZXgS1NQXGAvGLepY0-I', use_context=True)
    dispatcher = updater.dispatcher
    # handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, message_hand))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
