import sqlite3
import logging
import bs4
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('by')


class Client:

    def __init__(self):
        # Сесія зберігає стан між запитами (записує в себе coocies і тд..).
        # Підвищує вірогідність, що парсер не запідозрять
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
            'Accept-Language': 'uk'
        }

        self.description_str = ''

    def load_page(self, url):
        """Цей метод буде завантажувати сторінку"""
        res = self.session.get(url=url)
        # Перевіряє статус код-відповіді
        if res.status_code == 200:
            # Повертаємо текст сторінки в форматі HTML
            return res.text
        else:
            print(f'Запит {url} завершився з помилкою {res.status_code}')

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.tab-content')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        """Приймає на вхід об'єкт BS"""

        description_block = block.select_one('article.article')
        if not description_block:
            logger.error('no description_block')
            return

        description = block.select_one('p.article__description.content__txt.article__annotation')
        if not description:
            logger.error('no description')
            return

        text_description = description.get_text()
        if not text_description:
            logger.error('no text_description')

        logger.debug('%s', text_description)
        logger.debug('-' * 200)

        self.description_str = text_description

    def run(self):
        page = 0
        conn = sqlite3.connect('C:/Users/space/PycharmProjects/internet-literature-database/db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT url_book, description FROM main_book')
        results = cursor.fetchall()
        for row in results:
            if isinstance(row[0], str) and row[1] == '1':
                url = "https://book-ye.com.ua" + row[0]
                text = self.load_page(url)
                if text:
                    self.parse_page(text=text)
                    cursor.execute('UPDATE main_book SET description = ? WHERE url_book = ?', (self.description_str, row[0]))
                    page += 1
                    logger.info(f'Опрацювали {page} стор.')

                    conn.commit()

        conn.close()


if __name__ == '__main__':
    parser = Client()
    parser.run()

# Встановлюємо з'єднання з базою даних
# conn = sqlite3.connect('C:/Users/space/PycharmProjects/internet-literature-database/db.sqlite3')

# Створюємо курсор
# cursor = conn.cursor()

# Виконуємо запит до бази даних, щоб отримати дані зі стовпця "url_book"
# cursor.execute('SELECT url_book FROM main_book')
# results = cursor.fetchall()

# Обробляємо результат та записуємо дані у стовпець "description"
# for row in results:
# print(row)
# Обробляємо дані та записуємо їх у стовпець "column2"
# value = row[0] * 2  # Приклад обробки даних: множення на 2
# cursor.execute('UPDATE main_book SET description = ? WHERE main_book = ?', (value, row[0]))

# Зберігаємо зміни
# conn.commit()

# Закриваємо з'єднання з базою даних
# conn.close()
