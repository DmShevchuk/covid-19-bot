from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup
from bs4 import BeautifulSoup
import requests
import googletrans


def start(update, context):
    context.chat_data['activity'] = list()

    keyboard = [['Россия', 'США'], ['Мир', 'ТОП-10 стран'], ['Новые случаи в России'], ['Сайт по борьбе с коронавирусом']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text('🌍Введите название любой страны, я постараюсь предоставить статистику!\n\n'
                              '🎉 Нажмите на клавиатуре кнопку "Случайное развлечение", если не знаете,'
                              'чем себя занять\n\n', reply_markup=markup)


def message_hand(update, context):
    text = update.message.text.strip().lower()
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
                f'{latest_update[0].capitalize()}:\n' \
                f'{latest_update[1]}:{latest_update[2]}'

    return to_return


def country_handler(country):
    # Countries for quick search statistic
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
    translator = googletrans.Translator()

    source_lang = lang.split('-')[0]
    dest_lang = lang.split('-')[1]

    translated_text = translator.translate(text, src=source_lang, dest=dest_lang).text.lower()
    if len(translated_text.split()) < 5:
        translated_text = translated_text.split()
        translated_text = '-'.join(translated_text)

    return translated_text.strip()


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

    new_cases_ = '😷 Новых случаев: ' + cases[0] + '\n'
    new_deaths = '💀 Смертей: ' + cases[4] + '\n'

    return new_cases_ + new_deaths


def main():
    updater = Updater('', use_context=True)
    dispatcher = updater.dispatcher
    # handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, message_hand))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
